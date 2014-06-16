

def crawl_categories(id, page):

    try:

        parent_id = id
        main_category_check = False
        is_search_category = False
        top_level_parent = 0
        page_limit_cat = 30

        url = server_url + "/api/index.php/api/categories_api/getCategories?parent_id={0}&page={1}&limit={2}".format(id,
                                                                                                                     page,
                                                                                                                     page_limit_cat)
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        content = f.read()
        items = []

        print url

        if content:
            jsonObj = json.loads(content)
            totalCats = len(jsonObj)
            plugin.log.info('total categories-->%s' % totalCats)
            #plugin.log.info(jsonObj)

            for categories in jsonObj:

                #categories['id'] is -1 when more categories are present and next page option should be displayed
                if categories['id'] == -1:
                    items += [{
                                  'id':parent_id,
                                  'page':(int(page) + 1),
                                  'is_playable': False,
                              }]
                #categories['is_playable'] is False for all categories and True for all video Items
                elif categories['is_playable'] == 'False':

                    if categories['top_level_parent'] == '3' and categories['parent_id'] not in ('32', '3'):  # Parsing the TV Shows Titles & Seasons only
                        mvl_meta = ''
                        is_season = False
                        if 'parent_title' in categories:
                            #this must be a TV Show Season list
                            mvl_meta = create_meta('tvshow', categories['parent_title'].encode('utf-8'), '', '')
                        else:
                            mvl_meta = create_meta('tvshow', categories['title'].encode('utf-8'), '', '')

                    else:
                        crawl_categories(categories['id'], 0)

                #inorder for the information to be displayed properly, corresponding labels should be added in skin
                elif categories['is_playable'] == 'True':

                    if categories['video_id'] == '0':
                        #there is something wrong with this playable item. just ignore
                        continue

                    if categories['source'] == '1':
                        thumbnail_url = categories['image_name']
                    else:
                        thumbnail_url = server_url + '/wp-content/themes/twentytwelve/images/{0}'.format(categories['video_id'] + categories['image_name'])

                    mvl_img = thumbnail_url
                    series_name = 'NONE'

                    if categories['top_level_parent'] == '1':
                        mvl_meta = create_meta('movie', categories['title'].encode('utf-8'), categories['release_date'], mvl_img)
                    elif categories['top_level_parent'] == '3':
                        #playable items of TV show are episodes
                        mvl_meta = create_meta('episode', categories['title'].encode('utf-8'), categories['release_date'], mvl_img, categories['sub_categories_names'])

                        if 'series_name' in mvl_meta:
                            series_name = mvl_meta['series_name'].strip()

                    #plugin.log.info('>> meta data-> %s' % mvl_meta)

        return items

    except Exception, e:
        print 'Exception...'
        print e






ret = crawl_categories(1, 0)
#ret = crawl_categories(3, 0)

sys_exit()