#!/usr/bin/env python
from urllib.parse import urlparse, parse_qs

from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Blueprint
from sanic.response import html, text, redirect

from owllook.database.mongodb import MotorBase
from owllook.fetcher.cache import get_the_latest_chapter, cache_owllook_search_ranking, cache_others_search_ranking
from owllook.config import RULES, LOGGER, REPLACE_RULES, ENGINE_PRIORITY, CONFIG

md_bp = Blueprint('rank_blueprint', url_prefix='md')
md_bp.static('/static', CONFIG.BASE_DIR + '/static')


@md_bp.listener('before_server_start')
def setup_db(rank_bp, loop):
    global motor_base
    motor_base = MotorBase()


@md_bp.listener('after_server_stop')
def close_connection(rank_bp, loop):
    motor_base = None


# jinjia2 config
env = Environment(
    loader=PackageLoader('views.md_blueprint', '../templates'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@md_bp.route("/setting")
async def admin_setting(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            data = await motor_db.user.find_one({'user': user})
            if data:
                return template('admin_setting.html', title='{user}的设置 - owllook'.format(user=user),
                                is_login=1,
                                user=user,
                                register_time=data['register_time'],
                                email=data.get('email', '请尽快绑定邮箱'))
            else:
                return text('未知错误')
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@md_bp.route("/zh_bd_novels")
async def bd_novels(request):
    user = request['session'].get('user', None)
    first_type_title = "纵横百度小说月票榜"
    first_type = []
    title = "owllook - 纵横百度小说月票榜"
    novels_head = ['#', '小说名', '类型']
    search_ranking = await cache_others_search_ranking(spider='zh_bd_novels', novel_type='全部类别')
    if user:
        return template('index.html',
                        title=title,
                        is_login=1,
                        is_bd=1,
                        user=user,
                        search_ranking=search_ranking,
                        first_type=first_type,
                        first_type_title=first_type_title,
                        novels_head=novels_head)
    else:
        return template('index.html',
                        title=title,
                        is_login=0,
                        is_bd=1,
                        search_ranking=search_ranking,
                        first_type=first_type,
                        first_type_title=first_type_title,
                        novels_head=novels_head)


@md_bp.route("/book_list")
async def book_list(request):
    user = request['session'].get('user', None)
    if user:
        try:
            return template('admin_book_list.html', title='{user}的书单 - owllook'.format(user=user),
                            is_login=1,
                            user=user)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@md_bp.route("/bookmarks")
async def bookmarks(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            data = await motor_db.user_message.find_one({'user': user})
            if data:
                # 获取所有书签
                bookmarks = data.get('bookmarks', None)
                if bookmarks:
                    result = []
                    for i in bookmarks:
                        item_result = {}
                        bookmark = i.get('bookmark', None)
                        query = parse_qs(urlparse(bookmark).query)
                        item_result['novels_name'] = query.get('novels_name', '')[0] if query.get('novels_name',
                                                                                                  '') else ''
                        item_result['chapter_name'] = query.get(
                            'name', '')[0] if query.get('name', '') else ''
                        item_result['chapter_url'] = query.get('chapter_url', '')[0] if query.get('chapter_url',
                                                                                                  '') else ''
                        item_result['bookmark'] = bookmark
                        item_result['add_time'] = i.get('add_time', '')
                        result.append(item_result)
                    return template('admin_bookmarks.html', title='{user}的书签 - owllook'.format(user=user),
                                    is_login=1,
                                    user=user,
                                    is_bookmark=1,
                                    result=result[::-1])
            return template('admin_bookmarks.html', title='{user}的书签 - owllook'.format(user=user),
                            is_login=1,
                            user=user,
                            is_bookmark=0)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@md_bp.route("/books")
async def books(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            data = await motor_db.user_message.find_one({'user': user})
            if data:
                books_url = data.get('books_url', None)
                if books_url:
                    result = []
                    for i in books_url:
                        item_result = {}
                        book_url = i.get('book_url', None)
                        last_read_url = i.get("last_read_url", "")
                        book_query = parse_qs(urlparse(book_url).query)
                        last_read_chapter_name = parse_qs(
                            last_read_url).get('name', ['暂无'])[0]
                        item_result['novels_name'] = book_query.get('novels_name', '')[0] if book_query.get(
                            'novels_name', '') else ''
                        item_result['book_url'] = book_url
                        latest_data = await motor_db.latest_chapter.find_one({'owllook_chapter_url': book_url})
                        if latest_data:
                            item_result['latest_chapter_name'] = latest_data['data']['latest_chapter_name']
                            item_result['owllook_content_url'] = latest_data['data']['owllook_content_url']
                        else:
                            get_latest_data = await get_the_latest_chapter(book_url) or {}
                            item_result['latest_chapter_name'] = get_latest_data.get(
                                'latest_chapter_name', '暂未获取，请反馈')
                            item_result['owllook_content_url'] = get_latest_data.get(
                                'owllook_content_url', '')
                        item_result['add_time'] = i.get('add_time', '')
                        item_result["last_read_url"] = last_read_url if last_read_url else book_url
                        item_result["last_read_chapter_name"] = last_read_chapter_name
                        result.append(item_result)
                    return template('admin_books.html', title='{user}的书架 - owllook'.format(user=user),
                                    is_login=1,
                                    user=user,
                                    is_bookmark=1,
                                    result=result[::-1])
            return template('admin_books.html', title='{user}的书架 - owllook'.format(user=user),
                            is_login=1,
                            user=user,
                            is_bookmark=0)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@md_bp.route("/")
async def index(request):
    user = request['session'].get('user', None)
    novels_head = ['#', '小说名', '搜索次数']
    first_type_title = "搜索排行"
    first_type = []
    search_ranking = await cache_owllook_search_ranking()
    if user:
        return template('index.html', title='owllook', is_login=1, user=user, search_ranking=search_ranking,
                        first_type=first_type, first_type_title=first_type_title, novels_head=novels_head, is_owl=1)
    else:
        return template('index.html', title='owllook', is_login=0, search_ranking=search_ranking, first_type=first_type,
                        first_type_title=first_type_title, novels_head=novels_head, is_owl=1)


@md_bp.route("/noti_book")
async def noti_book(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            is_author = 0
            data = await motor_db.user_message.find_one({'user': user}, {'author_latest': 1, '_id': 0})
            if data:
                is_author = 1
                author_list = data.get('author_latest', {})
                return template('noti_book.html', title='新书提醒 - owllook'.format(user=user),
                                is_login=1,
                                is_author=is_author,
                                author_list=author_list,
                                user=user)
            else:
                return template('noti_book.html', title='新书提醒 - owllook'.format(user=user),
                                is_login=1,
                                is_author=is_author,
                                user=user)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@md_bp.route("/qidian")
async def qidian(request):
    user = request['session'].get('user', None)
    novels_type = request.args.get('type', '全部类别').strip()
    first_type_title = "全部类别"
    first_type = [
        '玄幻',
        '奇幻',
        '武侠',
        '仙侠',
        '都市',
        '职场',
        '军事',
        '历史',
        '游戏',
        '体育',
        '科幻',
        '灵异',
        '二次元',
    ]
    if novels_type in first_type:
        novels_head = [novels_type]
    elif novels_type == first_type_title:
        novels_head = ['#']
    else:
        return redirect('qidian')
    search_ranking = await cache_others_search_ranking(spider='qidian', novel_type=novels_type)
    title = "owllook - 起点小说榜单"
    if user:
        return template('novels/ranking.html',
                        title=title,
                        is_login=1,
                        is_qidian=1,
                        user=user,
                        search_ranking=search_ranking,
                        first_type=first_type,
                        first_type_title=first_type_title,
                        novels_head=novels_head)
    else:
        return template('novels/ranking.html',
                        title=title,
                        is_login=0,
                        is_qidian=1,
                        search_ranking=search_ranking,
                        first_type=first_type,
                        first_type_title=first_type_title,
                        novels_head=novels_head)


@md_bp.route("/similar_user")
async def similar_user(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            similar_info = await motor_db.user_recommend.find_one({'user': user})
            if similar_info:
                similar_user = similar_info['similar_user'][:20]
                user_tag = similar_info['user_tag']
                updated_at = similar_info['updated_at']
                return template('similar_user.html',
                                title='与' + user + '相似的书友',
                                is_login=1,
                                is_similar=1,
                                user=user,
                                similar_user=similar_user,
                                user_tag=user_tag,
                                updated_at=updated_at)
            else:
                return template('similar_user.html',
                                title='与' + user + '相似的书友',
                                is_login=1,
                                is_similar=0,
                                user=user)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')
