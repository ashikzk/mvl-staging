
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

        if content:
            jsonObj = json.loads(content)
            totalCats = len(jsonObj)
            plugin.log.info('total categories-->%s' % totalCats)
            plugin.log.info(jsonObj)
            #if jsonObj[0]['top_level_parent'] == jsonObj[0]['parent_id']:
            #    is_search_category = True

            for categories in jsonObj:
                try:    # The last item of Json only contains the one element in array with key as "ID" so causing the issue
                    if categories['top_level_parent'] == categories['parent_id']:
                        main_category_check = True

                except:
                    pass


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

                        items += [{
                                      'id':categories['id'],
                                      'page':0,
                                  }]

                    else:

                        items += [{
                                      'id':categories['id'],
                                      'page':0,
                                  }]

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

                    plugin.log.info('>> meta data-> %s' % mvl_meta)
                    thumbnail_url = ''

                    items += [{
                                'id': '-1'
                              }]


            #if main_category_check == True:
            #    #adding A-Z listing option
            #    items += [{
            #                  'label': button_label,
            #                  'path': plugin.url_for('azlisting', category=parent_id),
            #                  'thumbnail': art(button_name.lower()+'.png'),
            #                  'is_playable': False,
            #                  'context_menu': [('','',)],
            #                  'replace_context_menu': True
            #              }]
            #

        return items

    except Exception, e:
        print 'Exception...'
        print e




ret = crawl_categories(1, 0)

for r in ret:
    ret2 = crawl_categories(r['id'], r['page'])

print ret

sys_exit()