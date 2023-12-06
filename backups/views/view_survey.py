import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.conf import settings
from django.http import Http404

import backups.constant as constant

from secrets_content.files.secret_key import *

import pymongo
from bson.objectid import ObjectId
from .view_check import (
    get_logger,
    request_check_admin_role,
    request_check
)

logger = get_logger()

class SurveyViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        def __create_collection(db, name, validator):
            try:
                collection = db.create_collection(name)
                # db.command({
                #     'collMod': name,
                #     'validator': validator,
                #     'validationAction': 'error'
                # })
            except:
                collection = db.get_collection(name)
            return collection

        self.client = pymongo.MongoClient(SURVEY_DATABASES)

        if not settings.TESTING:
            self.db = self.client.get_database(constant.SURVEY_DB_NAME)
        else:
            self.db = self.client.get_database(os.environ.get("TEST_DB_NAME", 'test'))
        self.collection_survey = __create_collection(self.db, constant.SURVEY_POST_DB_NME, None)
        self.collection_quiz = __create_collection(self.db, constant.SURVEY_QUIZ, None)
        self.collection_answer = __create_collection(self.db, constant.SURVEY_ANSWER, None)

    def create_post(self, request):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            logger.debug(f'{user_uid} Survey Post post approved')
            post_data = request.data
            try:
                created_time = datetime.datetime.now()
                to = None
                # if 'to_time' in post_data:
                #     to = datetime.datetime.strptime(post_data['to_time'], constant.TIME_QUERY)
                # print(post_data)
                survey_data = {
                    '_id': ObjectId(),
                    'title': post_data['title'],
                    'description': post_data['description'],
                    'role': int(post_data['role']),
                    'activate': int(post_data['activate']),
                    'created_time': created_time,
                    'modified_time': created_time,
                }
                # if to is not None:
                #     assert created_time < to, 'The last day must be later than the start date.'
                #     survey_data['to_time'] = to

                quizzes = post_data['quizzes']
                assert len(quizzes), "There must be at least one question."
                assert len(quizzes) <= 60, "There must be no more than 60 questions."

                quizzes_data = []
                for q in quizzes:
                    type = int(q['type'])
                    quiz_data = {
                        '_id': ObjectId(),
                        'parent_post': survey_data['_id'],
                        'title': q['title'],
                        'description': q['description'],
                        'require': int(q['require']),
                        'type': type
                    }
                    # post
                    if type == constant.SURVEY_TEXT_CODE:  # text, current: 0
                        pass
                    elif type == constant.SURVEY_SELECT_ONE_CODE:  # select one, current: 1
                        quiz_data['options'] = []
                        for i in q['options']:
                            quiz_data['options'].append({
                                'text': i['text']
                            })
                        assert len(quiz_data) > 0, 'There must be at least one option.'
                    elif type == constant.SURVEY_SELECT_MULTIPLE_CODE: #select multiple, current: 2
                        quiz_data['options'] = []
                        for i in q['options']:
                            quiz_data['options'].append({
                                'text': i['text']
                            })
                        assert len(quiz_data) > 0, 'There must be at least one option.'
                    else:
                        assert False, f'{type} is a non-existent question type.'
                    quizzes_data.append(quiz_data)

                survey_result = self.collection_survey.insert_one(survey_data)
                quizzes_result = self.collection_quiz.insert_many(quizzes_data)

                response_data = survey_data
                response_data['quizzes'] = []
                response_data['_id'] = str(response_data['_id'])
                response_data['created_time'] = response_data['created_time'].strftime(constant.TIME_QUERY)
                response_data['modified_time'] = response_data['modified_time'].strftime(constant.TIME_QUERY)
                for q in quizzes_data:
                    q['_id'] = str(q['_id'])
                    q['parent_post'] = str(q['parent_post'])
                    response_data['quizzes'].append(q)

                update_log = f'{user_uid} Survey Post data created' \
                             f'\tkey: {response_data["_id"]}: created log'
                for k in response_data.keys():
                    if k == 'quizzes': continue
                    update_log += f'\n\t{k} {response_data[k]}'
                logger.info(update_log)
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f'create survey post failed.\n\terror: {e}')
                detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-001",

                        "message": "create survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"{user_uid} Survey Post create denied")
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 403,

                        "error": "Forbidden",

                        "code": "JGW_hub-survey-002",

                        "message": "Survey Post create denied",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    def create_answer(self, request, pk):
        checked = request_check(request)
        if isinstance(checked, Response):
            # user role이 없다면 최하위 권한 적용
            user_role_id = -1
            user_uid = None
        else:
            user_uid, user_role_id = checked
        try:
            request_data = request.data
            survey_data = self.collection_survey.find_one({'_id': ObjectId(pk)})
            assert survey_data['role'] <= int(user_role_id), "User is not a survey participant."
            logger.debug(f'{user_uid} Answer post approved')

            quizzes_data = self.collection_quiz.find({'parent_post': ObjectId(pk)})
            quizzes_data = list(quizzes_data)
            answers = request_data['answers']
            assert len(answers) == len(quizzes_data), "The number of responses must equal the number of questions."

            answer_data = {
                '_id': ObjectId(),
                'parent_post': ObjectId(pk),
                'user': user_uid,
                'answers': []
            }
            for idx, q in enumerate(quizzes_data):
                a = answers[idx]
                type = int(a['type'])
                assert q['type'] == a['type'], f'The data format of the response is different from the question. idx" {idx}'

                answer = {
                    "parent_quiz": q['_id']
                }

                if 'null' in a:
                    if int(q['require']) == 0 and int(a['null']) == 1:
                        answer['null'] = 1
                        answer_data['answers'].append(answer)
                        continue
                    elif int(q['require']) == 1 and int(a['null']) == 1:
                        assert False, 'Required response questions must be answered.'

                # create answer
                if type == constant.SURVEY_TEXT_CODE:
                    answer['text'] = a['text']
                elif type == constant.SURVEY_SELECT_ONE_CODE:
                    selection = int(a['selection'])
                    assert selection < len(q['options']), 'An option that does not exist.'
                    answer['selection'] = selection
                elif type == constant.SURVEY_SELECT_MULTIPLE_CODE:
                    selections = sorted(list(set(map(int, a['selections']))))
                    assert len(selections) > 0, 'There must be at least one option selected.'
                    assert len(selections) <= len(q['options']), 'An option that does not exist.'
                    assert selections[-1] < len(q['options']), 'An option that does not exist.'
                    answer['selections'] = selections
                else:
                    assert False, f'{type} is a non-existent answer type.'
                answer_data['answers'].append(answer)
            assert len(answer_data['answers']) == len(quizzes_data), "Invalid response data exists."
            # print(answer_data)

            if user_uid is not None:
                self.collection_answer.delete_one({'parent_post': ObjectId(pk), 'user': user_uid})
            self.collection_answer.insert_one(answer_data)

            answer_data['_id'] = str(answer_data['_id'])
            answer_data['parent_post'] = str(answer_data['parent_post'])
            for a in answer_data['answers']:
                a['parent_quiz'] = str(a['parent_quiz'])

            update_log = f'{user_uid} Answer data created' \
                         f'\tkey: {answer_data["_id"]}\tparent post key: {answer_data["parent_post"]} created log'
            for ans in answer_data['answers']:
                update_log += f'\n\tparent_quiz: {ans["parent_quiz"]}'
            logger.info(update_log)
            return Response(answer_data, status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'create answer failed.\n\terror: {e}')
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-003",

                        "message": "create answer failed",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    def list_post(self, request):
        checked = request_check(request)
        if isinstance(checked, Response):
            # user role이 없다면 최하위 권한 적용
            user_role_id = -1
            user_uid = None
        else:
            user_uid, user_role_id = checked
        logger.debug(f"Survey Post get request")
        try:
            request.query_params._mutable = True

            target_title = ''
            if 'title' in request.query_params:
                target_title = request.query_paramsp['title']
            aggregate_dict = [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {'$lte': ['$role', user_role_id]}
                            ]
                        }
                    }},
                {'$match': {'title': {'$regex': target_title}}},
                {
                    '$sort': {
                        'activate': -1,
                        'created_time': -1
                    }
                },
                {'$count': 'count'}
            ]
            print(list(self.collection_survey.aggregate(aggregate_dict)), user_role_id, target_title)
            total_count = list(self.collection_survey.aggregate(aggregate_dict))
            if total_count:
                total_count = total_count[-1]['count']
            else:
                total_count = 0
            del aggregate_dict[-1]

            if 'page_size' in request.query_params:
                # page size를 최소~최대 범위 안에서 지정
                request.query_params['page_size'] = int(request.query_params['page_size'])
                if request.query_params['page_size'] < constant.SURVEY_MIN_PAGE_SIZE:
                    request.query_params['page_size'] = constant.SURVEY_MIN_PAGE_SIZE
                elif request.query_params['page_size'] > constant.SURVEY_MAX_PAGE_SIZE:
                    request.query_params['page_size'] = constant.SURVEY_MAX_PAGE_SIZE
            else:
                request.query_params['page_size'] = constant.SURVEY_DEFAULT_PAGE_SIZE

            max_page = total_count // request.query_params['page_size']
            max_page += 1 if total_count % request.query_params['page_size'] else 0
            if 'page' not in request.query_params:
                # page를 지정하지 않으면 1로 지정
                request.query_params['page'] = 1
            else:
                request.query_params['page'] = int(request.query_params['page'])
                if request.query_params['page'] < 1:
                    request.query_params['page'] = 1
                elif max_page < request.query_params['page']:
                    request.query_params['page'] = max_page

            aggregate_dict.append({'$skip': (request.query_params['page'] - 1) * request.query_params['page_size']})
            aggregate_dict.append({'$limit': request.query_params['page_size']})
            page_now = self.collection_survey.aggregate(aggregate_dict)
            page_now = list(page_now)

            response_data = {
                'count': len(page_now),
                'total_pages': max_page,
                'next': request.build_absolute_uri().split('?')[0] +
                        f'page={request.query_params["page"] + 1}&page_size={request.query_params["page_size"]}'
                        if request.query_params['page'] < max_page else None,
                'previous': request.build_absolute_uri().split('?')[0] +
                            f'page={request.query_params["page"] - 1}&page_size={request.query_params["page_size"]}'
                            if request.query_params['page'] > 1 else None,
                'results': []
            }

            for d in page_now:
                d['_id'] = str(d['_id'])
                d['created_time'] = d['created_time'].strftime(constant.TIME_QUERY)
                d['modified_time'] = d['modified_time'].strftime(constant.TIME_QUERY)
            response_data['results'] = page_now
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'get list survey post failed.\n\terror: {e}')
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-004",

                        "message": "get list survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    def retrieve_post(self, request, pk):
        checked = request_check(request)
        if isinstance(checked, Response):
            # user role이 없다면 최하위 권한 적용
            user_role_id = -1
            user_uid = None
        else:
            user_uid, user_role_id = checked
        try:
            survey_data = self.collection_survey.find_one({'_id': ObjectId(pk)})
            if survey_data is None: raise Http404('Data does not exist.')

            assert survey_data['role'] <= user_role_id, 'User is not a survey participant.'
            logger.debug(f'{user_uid} Survey Post retrieve approved')

            quizzes_data = self.collection_quiz.find(({'parent_post': ObjectId(pk)}))
            quizzes_data = list(quizzes_data)

            response_data = survey_data
            response_data['quizzes'] = []
            response_data['_id'] = str(response_data['_id'])
            response_data['created_time'] = response_data['created_time'].strftime(constant.TIME_QUERY)
            response_data['modified_time'] = response_data['modified_time'].strftime(constant.TIME_QUERY)
            for q in quizzes_data:
                q['_id'] = str(q['_id'])
                q['parent_post'] = str(q['parent_post'])
                response_data['quizzes'].append(q)

            logger.debug(f'{user_uid} Survey Post data get retrieve\tkey: {pk}\ttitle: {response_data["title"]}')
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404 as e:
            logger.error(f'retrieve survey post failed.\n\terror: {e}')
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 404,

                        "error": str(e),

                        "code": "JGW_hub-survey-005",

                        "message": "retrieve survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'retrieve survey post failed.\n\terror: {e}')
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-006",

                        "message": "retrieve survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    def list_answers(self, request, pk):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            logger.debug(f'{user_uid} Survey Answers list approved')
            if 'analyze' in request.query_params and int(request.query_params['analyze']) == 1: # 분석 요청
                logger.debug(f'{user_uid} Survey Answers list analyze request')
                try:
                    assert 'answer_id' in request.query_params, 'The id of the response to be analyzed is required.'
                    answer_id = request.query_params['answer_id']

                    quiz_data = list(self.collection_quiz.aggregate([
                        {"$match": {'parent_post': ObjectId(pk), '_id': ObjectId(answer_id)}}
                    ]))

                    assert len(quiz_data) > 0, 'There are no questions.'
                    quiz_data = quiz_data[0]

                    quiz_type = quiz_data['type']
                    if quiz_type == constant.SURVEY_TEXT_CODE:
                        total_count = list(self.collection_answer.aggregate([
                            {'$unwind': '$answers'},
                            {'$match': {'answers.parent_quiz': ObjectId(answer_id)}},
                            {'$count': 'answers'}
                        ]))[0]['answers']

                        page_size = constant.ANSWER_DEFAULT_PAGE_SIZE
                        if 'page_size' in request.query_params:
                            # page size를 최소~최대 범위 안에서 지정
                            page_size = int(request.query_params['page_size'])
                            if page_size < constant.ANSWER_MIN_PAGE_SIZE:
                                page_size = constant.ANSWER_MIN_PAGE_SIZE
                            elif page_size > constant.ANSWER_MAX_PAGE_SIZE:
                                page_size = constant.ANSWER_MAX_PAGE_SIZE

                        max_page = total_count // page_size
                        max_page += 1 if total_count % page_size else 0
                        if 'page' not in request.query_params:
                            # page를 지정하지 않으면 1로 지정
                            page = 1
                        else:
                            page = int(request.query_params['page'])
                            if page < 1:
                                page = 1
                            elif max_page < page:
                                page = max_page

                        results = list(self.collection_answer.aggregate([
                            {'$unwind': '$answers'},
                            {'$match': {'answers.parent_quiz': ObjectId(answer_id)}},
                            {'$project': {'_id': 0, 'text': '$answers.text'}},
                            {'$skip': (page - 1) * page_size},
                            {'$limit': page_size}
                        ]))

                        response_data = {
                            'count': len(results),
                            'total_pages': max_page,
                            'next': request.build_absolute_uri().split('?')[0] +
                                    f'page={page + 1}&page_size={page_size}'
                            if page < max_page else None,
                            'previous': request.build_absolute_uri().split('?')[0] +
                                        f'page={page - 1}&page_size={page_size}'
                            if page > 1 else None,
                            'results': results
                        }
                        return Response(response_data, status=status.HTTP_200_OK)
                    elif quiz_type == constant.SURVEY_SELECT_ONE_CODE:
                        results = self.collection_quiz.aggregate([
                            {'$match': {'_id': quiz_data['_id']}},
                            {'$project': {'options': '$options.text'}},
                            {'$unwind': {'path': '$options', 'includeArrayIndex': 'idx'}},
                            {'$lookup': {
                                'from': 'survey_answer',
                                'let': {
                                    'quiz_id': '$_id',
                                    'quiz_idx': '$idx'
                                },
                                'pipeline': [
                                    {'$unwind': '$answers'},
                                    {'$match': {
                                            '$expr': {
                                                '$and': [
                                                    {'$eq': ['$answers.parent_quiz', '$$quiz_id']},
                                                    {'$eq': ['$answers.selection', '$$quiz_idx']}
                                                ]
                                            }
                                        }
                                    }, {
                                        '$project': {
                                            '_id': 0,
                                            'answers': 1
                                        }
                                    }, {
                                        '$count': 'selected'
                                    }
                                ],
                                'as': 'aaa'}},
                            {'$project': {
                                '_id': 0,
                                'text': '$options',
                                'idx': 1,
                                'count': {
                                    '$cond': [{'$anyElementTrue': '$aaa.selected'},
                                              {'$arrayElemAt': ['$aaa.selected', 0]}, 0]
                                }}
                            }
                        ])
                        results = list(results)
                        return Response(results, status=status.HTTP_200_OK)
                    elif quiz_type == constant.SURVEY_SELECT_MULTIPLE_CODE:
                        results = self.collection_quiz.aggregate([
                            {'$match': {'_id': quiz_data['_id']}},
                            {'$project': {'options': '$options.text'}},
                            {'$unwind': {'path': '$options', 'includeArrayIndex': 'idx'}},
                            {'$lookup': {
                                'from': 'survey_answer',
                                'let': {
                                    'quiz_id': '$_id',
                                    'quiz_idx': '$idx'
                                },
                                'pipeline': [
                                    {'$unwind': '$answers'},
                                    {'$match': {
                                            '$expr': {
                                                '$and': [
                                                    {'$eq': ['$answers.parent_quiz', '$$quiz_id']},
                                                    {'$in': ['$$quiz_idx', '$answers.selections']}
                                                ]
                                            }
                                        }
                                    }, {
                                        '$project': {
                                            '_id': 0,
                                            'answers': 1
                                        }
                                    }, {
                                        '$count': 'selected',
                                }
                                ],
                                'as': 'aaa'}},
                            {'$project': {
                                '_id': 0,
                                'text': '$options',
                                'idx': 1,
                                'count': {
                                    '$cond': [{'$anyElementTrue': '$aaa.selected'},
                                              {'$arrayElemAt': ['$aaa.selected', 0]}, 0]
                                }}
                            }
                        ])
                        results = list(results)
                        # print(results)
                        return Response(results, status=status.HTTP_200_OK)
                    else:
                        assert False, 'Error in question data.'
                except Exception as e:
                    logger.error(f'get list survey answers analyze failed.\n\terror: {e}')
                    detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-007",

                        "message": "get list survey answers analyze failed",

                        "path": "/hub/api/v1/survey/"
                    }
                    return Response(detail, status=status.HTTP_400_BAD_REQUEST)
            else: # 사용자별 데이터 요청
                logger.debug(f'{user_uid} Survey Answers list user request')
                try:
                    total_count = list(self.collection_answer.aggregate([
                        {'$project': {'parent_post': ObjectId(pk)}},
                        {'$count': 'answers'}
                    ]))[0]['answers']

                    page_size = constant.ANSWER_DEFAULT_PAGE_SIZE
                    if 'page_size' in request.query_params:
                        # page size를 최소~최대 범위 안에서 지정
                        page_size = int(request.query_params['page_size'])
                        if page_size < constant.ANSWER_MIN_PAGE_SIZE:
                            page_size = constant.ANSWER_MIN_PAGE_SIZE
                        elif page_size > constant.ANSWER_MAX_PAGE_SIZE:
                            page_size = constant.ANSWER_MAX_PAGE_SIZE

                    max_page = total_count // page_size
                    max_page += 1 if total_count % page_size else 0
                    if 'page' not in request.query_params:
                        # page를 지정하지 않으면 1로 지정
                        page = 1
                    else:
                        page = int(request.query_params['page'])
                        if page < 1:
                            page = 1
                        elif max_page < page:
                            page = max_page

                    # print(page, page_size)

                    target_answers = self.collection_answer.find({'parent_post': ObjectId(pk)}) \
                        .skip((page - 1) * page_size) \
                        .limit(page_size)
                    target_answers = list(target_answers)

                    response_data = {
                        'count': len(target_answers),
                        'total_pages': max_page,
                        'next': request.build_absolute_uri().split('?')[0] +
                                f'page={page + 1}&page_size={page_size}'
                                if page < max_page else None,
                        'previous': request.build_absolute_uri().split('?')[0] +
                                    f'page={page - 1}&page_size={page_size}'
                                    if page > 1 else None,
                        'results': []
                    }

                    for d in target_answers:
                        d['_id'] = str(d['_id'])
                        d['parent_post'] = str(d['parent_post'])
                        for a in d['answers']:
                            a['parent_quiz'] = str(a['parent_quiz'])
                    response_data['results'] = target_answers
                    return Response(response_data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f'get list survey answers user failed.\n\terror: {e}')
                    detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-008",

                        "message": "get list survey answers user failed",

                        "path": "/hub/api/v1/survey/"
                    }
                    return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"{user_uid} Survey Answers list denied")
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 403,

                        "error": "Forbidden",

                        "code": "JGW_hub-survey-009",

                        "message": "Survey Answers list denied",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    def delete_post(self, request, pk):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            logger.debug(f'{user_uid} Survey Post delete approved')
            try:
                result_post = self.collection_survey.delete_one({'_id': ObjectId(pk)})
                result_quiz = self.collection_quiz.delete_many({'parent_post': ObjectId(pk)})
                result_answer = self.collection_answer.delete_many({'parent_post': ObjectId(pk)})
                logger.debug(f'{user_uid} Survey Post data deleted\tkey: {pk}\tquiz count: {result_quiz.deleted_count}'
                             f'\tanswer count: {result_answer.deleted_count}')
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                logger.error(f'delete survey post failed.\n\terror: {e}')
                detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-010",

                        "message": "delete survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"{user_uid} Survey Post delete denied")
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 403,

                        "error": "Forbidden",

                        "code": "JGW_hub-survey-011",

                        "message": "Survey Post delete denied",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)

    def patch_post(self, request, pk):
        checked = request_check_admin_role(request)
        if isinstance(checked, Response):
            # 요청한 유저 정보가 없다면 500 return
            return checked
        user_uid, user_role_id, admin_role_checked = checked
        if user_role_id >= admin_role_checked:
            logger.debug(f'{user_uid} Survey Post patch approved')
            try:
                before_patch = self.collection_survey.find_one({'_id': ObjectId(pk)})
                assert before_patch is not None, 'Survey data not found'

                request_data = request.data
                update_data = {}
                if 'title' in request_data:
                    update_data['title'] = request_data['title']
                if 'description' in request_data:
                    update_data['description'] = request_data['description']
                if 'role' in request_data:
                    update_data['role'] = int(request_data['role'])
                if 'activate' in request_data:
                    update_data['activate'] = int(request_data['activate'])
                assert len(update_data) > 0, 'You must have at least one data to update.'
                update_data['modified_time'] = datetime.datetime.now()

                patch_result = self.collection_survey.update_one(
                    {'_id': ObjectId(pk)},
                    {'$set': update_data}
                )
                after_patch = self.collection_survey.find_one({'_id': ObjectId(pk)})

                update_log = f'{user_uid} Survey Post data patched' \
                             f'\tkey: {pk} change log'
                for k in update_data.keys():
                    instance_data = after_patch[k]
                    before_change = before_patch[k]
                    if k in ('title', 'description'):
                        instance_data = instance_data[:50]
                        before_change = before_change[:50]
                    update_log += f'\n\t{k}: {before_change} -> {instance_data}'
                # logger.info(update_log)

                after_patch['_id'] = str(after_patch['_id'])
                after_patch['created_time'] = after_patch['created_time'].strftime(constant.TIME_QUERY)
                after_patch['modified_time'] = after_patch['modified_time'].strftime(constant.TIME_QUERY)
                # print(after_patch)

                return Response(after_patch, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'patch survey post failed.\n\terror: {e}')
                detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 400,

                        "error": str(e),

                        "code": "JGW_hub-survey-012",

                        "message": "patch survey post failed",

                        "path": "/hub/api/v1/survey/"
                    }
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"{user_uid} Survey Post patch denied")
            detail = {
                        "timestamp": datetime.datetime.now().isoformat(),

                        "status": 403,

                        "error": "Forbidden",

                        "code": "JGW_hub-survey-013",

                        "message": "Survey Post patch denied",

                        "path": "/hub/api/v1/survey/"
                    }
            return Response(detail, status=status.HTTP_403_FORBIDDEN)
