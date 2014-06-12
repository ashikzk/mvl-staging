def get_categories(id, page):

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
                # plugin.log.info(jsonObj)
                if jsonObj[0]['top_level_parent'] == jsonObj[0]['parent_id']:
                    is_search_category = True

                for categories in jsonObj:
                    try:    # The last item of Json only contains the one element in array with key as "ID" so causing the issue
                        if categories['top_level_parent'] == categories['parent_id']:
                            main_category_check = True

                    except:
                        pass

                    if is_search_category == True:
                        is_search_category = False

                        if categories['parent_id'] == '1':
                            button_name = 'SearchMovies1'
                            button_label = 'Search Movies'
                        elif categories['parent_id'] == '3':
                            button_name = 'SearchTVShows1'
                            button_label = 'Search TV Shows'

                        #adding search option
                        items += [{
                                  'label': button_label,
                                  'path': plugin.url_for('search', category=parent_id),
                                  'thumbnail': art(button_name.lower()+'.png'),
                                  'is_playable': False,
                                  'context_menu': [('','',)],
                                  'replace_context_menu': True
                                  }]

                    ####
                    #add an extra item for the release month + year combo
                    if 'release_group' in categories:
                        if categories['release_group'] != last_release_group:
                            if last_release_group == '':
                                #that means this is the first line of list
                                items += [{
                                              'label': '[COLOR FFC41D67]Estimated Release Date[/COLOR]',
                                              'path': plugin.url_for('do_nothing', view_mode=0),
                                              'is_playable': False,
                                              'context_menu': [('','',)],
                                              'replace_context_menu': True
                                          }]


                            last_release_group = categories['release_group']

                            items += [{
                                          'label': categories['release_group'],
                                          'path': plugin.url_for('do_nothing', view_mode=0),
                                          'is_playable': False,
                                          'context_menu': [('','',)],
                                          'replace_context_menu': True
                                      }]

                    ####

                    #categories['id'] is -1 when more categories are present and next page option should be displayed
                    if categories['id'] == -1:
                        items += [{
                                      'label': 'Next >>',
                                      'path': plugin.url_for('get_categories', id=parent_id, page=(int(page) + 1)),
                                      'is_playable': False,
                                      'thumbnail': art('next.png'),
                                      'context_menu': [('','',)],
                                      'replace_context_menu': True
                                  }]
                    #categories['is_playable'] is False for all categories and True for all video Items
                    elif categories['is_playable'] == 'False':

                        if categories['top_level_parent'] == '3' and categories['parent_id'] not in ('32', '3'):  # Parsing the TV Shows Titles & Seasons only
                            mvl_meta = ''
                            #tmpTitle = categories['title'].encode('utf-8')
                            #if tmpTitle == "Season 1":
                            #    tmpSeasons = []
                            #    mvl_view_mode = 50
                                # for i in range(totalCats):
                                # tmpSeasons.append( i )
                                #plugin.log.info('season found')
                                #mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
                            is_season = False
                            if 'parent_title' in categories:
                                #this must be a TV Show Season list
                                mvl_meta = create_meta('tvshow', categories['parent_title'].encode('utf-8'), '', '')
                                mvl_tvshow_title = categories['parent_title'].encode('utf-8')
                                is_season = True
                                #xbmcplugin.setContent(pluginhandle, 'Seasons')

                            else:
                                mvl_meta = create_meta('tvshow', categories['title'].encode('utf-8'), '', '')
                                mvl_tvshow_title = categories['title'].encode('utf-8')

                            dp_type = 'show'

                            #plugin.log.info('meta data-> %s' % mvl_meta)

                            thumbnail_url = ''
                            try:
                                if mvl_meta['cover_url']:
                                    thumbnail_url = mvl_meta['cover_url']
                            except:
                                thumbnail_url = ''

                            #print "New Thumb"
                            #print thumbnail_url

                            fanart_url = ''
                            try:
                                if mvl_meta['backdrop_url']:
                                    fanart_url = mvl_meta['backdrop_url']
                            except:
                                fanart_url = ''

                            mvl_plot = ''
                            try:
                                if mvl_meta['plot']:
                                    mvl_plot = mvl_meta['plot']
                            except:
                                mvl_plot = ''

                            if is_season:
                                info_dic = {
                                        'title': categories['title'].encode('utf-8'),
                                        }
                            else:
                                info_dic = {
                                          'title': categories['title'].encode('utf-8'),
                                          'rating': mvl_meta['rating'],
                                          'plot': mvl_plot,
                                          'year': mvl_meta['year'],
                                          'premiered': mvl_meta['premiered'],
                                          'duration': mvl_meta['duration']
                                          }

                            items += [{
                                          'label': '{0}'.format(categories['title'].encode('utf-8')),
                                          'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': thumbnail_url,
                                          'properties': {
                                              'fanart_image': fanart_url,
                                          },
                                          'info': info_dic,
                                          'context_menu': [('','',)],
                                          'replace_context_menu': True
                                      }]

                        else:

                            button_name = categories['title']
                            button_category = categories['parent_id']

                            if categories['parent_id'] == '1':
                                if categories['title'] == 'New Releases':
                                    button_name = 'DateReleased1'
                                    categories['title'] = 'Date Released'
                                elif categories['title'] == 'Featured':
                                    button_name = 'Cinema1'
                                    categories['title'] = 'Cinema Movies'
                                elif categories['title'] == 'Genre':
                                    button_name = 'MovieGenres2'
                                    categories['title'] = 'Movies by Genre'
                            elif categories['parent_id'] == '3':
                                if categories['title'] == 'New Releases':
                                    button_name = 'DateAired1'
                                    categories['title'] = 'Recently Aired'
                                elif categories['title'] == 'Featured':
                                    button_name = 'PopularTV1'
                                    categories['title'] = 'Popular TV Series'
                                elif categories['title'] == 'Genre':
                                    button_name = 'TVByGenres1'
                                    categories['title'] = 'TV Shows by Genre'

                            items += [{
                                          'label': '{0}'.format(categories['title'].encode('utf-8')),
                                          'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': art('{0}.png'.format(button_name.lower())),
                                          'context_menu': [('','',)],
                                          'replace_context_menu': True
                                      }]

                            # print button_name.lower()


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

                        watch_info = {'video_type': 'movie', 'season': 'NONE', 'episode': 'NONE', 'year': '0'}

                        if categories['top_level_parent'] == '1':
                            mvl_meta = create_meta('movie', categories['title'].encode('utf-8'), categories['release_date'], mvl_img)
                            watch_info['year'] = mvl_meta['year']
                        elif categories['top_level_parent'] == '3':
                            #playable items of TV show are episodes
                            mvl_meta = create_meta('episode', categories['title'].encode('utf-8'), categories['release_date'], mvl_img, categories['sub_categories_names'])

                            watch_info['video_type'] = 'episode'
                            watch_info['season'] = mvl_meta['season']
                            watch_info['episode'] = mvl_meta['episode']
                            watch_info['year'] = mvl_meta['premiered'][:4]

                            if watch_info['year'] == '':
                                watch_info['year'] = 0


                            if 'series_name' in mvl_meta:
                                series_name = mvl_meta['series_name'].strip()
                            #set layout to Episode
                            xbmcplugin.setContent(pluginhandle, 'Episodes')


                        plugin.log.info('>> meta data-> %s' % mvl_meta)
                        thumbnail_url = ''

                        dp_type = 'movie'

                        try:
                            if mvl_meta['cover_url']:
                                thumbnail_url = mvl_meta['cover_url']
                        except:
                            thumbnail_url = mvl_img

                        # New condition added
                        if thumbnail_url == '':
                            thumbnail_url = art('image-not-available.png')
                        fanart_url = ''
                        try:
                            if mvl_meta['backdrop_url']:
                                fanart_url = mvl_meta['backdrop_url']
                        except:
                            fanart_url = ''

                        mvl_plot = ''
                        try:
                            if mvl_meta['plot']:
                                mvl_plot = mvl_meta['plot']
                        except:
                            mvl_plot = categories['synopsis'].encode('utf-8')

                        watched_state = 'Watched'
                        if mvl_meta['playcount'] > 0:
                            watched_state = 'Unwatched'

                        items += [{
                                      'thumbnail': thumbnail_url,
                                      'properties': {
                                          'fanart_image': fanart_url,
                                      },
                                      'label': '{0}'.format(categories['title'].encode('utf-8')),
                                      'info': {
                                          'title': categories['title'].encode('utf-8'),
                                          'rating': categories['rating'],
                                          'comment': categories['synopsis'].encode('utf-8'),
                                          'Director': categories['director'].encode('utf-8'),
                                          'Producer': categories['producer'],
                                          'Writer': categories['writer'],
                                          'plot': mvl_plot,
                                          'genre': categories['sub_categories_names'],
                                          'cast': categories['actors'].encode('utf-8'),
                                          'year': categories['release_date'],
                                          'premiered': categories['release_date'],
                                          'duration': mvl_meta['duration'],
                                          'playcount': mvl_meta['playcount']
                                      },
                                      'path': plugin.url_for('get_videos', id=categories['video_id'],
                                                             thumbnail=thumbnail_url, trailer=get_trailer_url(mvl_meta).encode('utf-8'),
                                                             parent_id=categories['top_level_parent'], series_name=series_name),
                                      'is_playable': False,
                                      'context_menu': [(
                                                           'Mark as {0}'.format(watched_state),
                                                           'XBMC.RunPlugin(%s)' % plugin.url_for('mark_as_{0}'.format(watched_state.lower()),
                                                                                                 video_type=watch_info['video_type'],
                                                                                                 title=categories['title'].encode('utf-8'),
                                                                                                 imdb_id=mvl_meta['imdb_id'],
                                                                                                 year=watch_info['year'],
                                                                                                 season=watch_info['season'],
                                                                                                 episode=watch_info['episode']
                                                                                                 )
                                                       )],
                                      'replace_context_menu': True
                                  }]

                    if categories['id'] != -1:
                        if categories['top_level_parent'] == '1':
                            dp_type = 'movie'
                        elif categories['top_level_parent'] == '3':
                            dp_type = 'show'

                    if dp_created == False:
                        dp.create("Please wait while "+dp_type+" list is loaded","","")
                        dp_created = True

                    done_count = done_count + 1
                    dp.update((done_count*100/item_count), str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")

                    if dp.iscanceled():
                        break



                if main_category_check == True:
                    #adding A-Z listing option
                    if button_category == '1':
                        button_name = 'AZMovies1'
                        button_label = 'Movies A-Z'
                    elif button_category == '3':
                        button_name = 'AZTvShows1'
                        button_label = 'TV Shows A-Z'

                    items += [{
                                  'label': button_label,
                                  'path': plugin.url_for('azlisting', category=parent_id),
                                  'thumbnail': art(button_name.lower()+'.png'),
                                  'is_playable': False,
                                  'context_menu': [('','',)],
                                  'replace_context_menu': True
                              }]
                    #Most Popular & Favortite are commented out on Client's request for now
                    #adding Most Popular option
                    # items += [{
                    # 'label': 'Most Popular',
                    # 'path': plugin.url_for('mostpopular', page=0, category=parent_id),
                    # 'thumbnail' : art('pop.png'),
                    # 'is_playable': False,
                    # }]
                    # #adding Favourites option
                    # items += [{
                    # 'label': 'Favourites',
                    # 'path': plugin.url_for('get_favourites', category=parent_id),
                    # 'thumbnail' : art('fav.png'),
                    # 'is_playable': False,
                    # }]
                #plugin.log.info(items)

                dp.close()


            #we should set the view_mode as last thing in this method
            #because if user cancels his action and goes back before the api response
            #the view_mode will still be changed otherwise
            if id in ('23', '32'): # if the Parent ID is Genres for TV or Movies then view should be set as "List" mode
                mvl_view_mode = 50
            elif id in ('1', '3'):  # if these are immediate childs of Top Level parents then view should be set as Fan Art
                mvl_view_mode = 59
            # else:
                # mvl_view_mode = 59

            hide_busy_dialog()

            #plugin.log.info("View mode = " + str(mvl_view_mode))
            #set current section name
            if id == '1':
                xbmc.executebuiltin('Skin.SetString(CurrentSection,Movies)')
            elif id == '3':
                xbmc.executebuiltin('Skin.SetString(CurrentSection,TV)')


            return items
        # except IOError:
            # xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
        except Exception, e:
            print 'Exception...'
            print e

            if id in ('1', '3'):  # if we were on 1st page, then the viewmode should remain to 58 as an error has occured and we haven't got any data for next screen
                mvl_view_mode = 58
            elif id in ('23', '104916', '112504', '32', '104917', '366042', '372395', '372396'):
                mvl_view_mode = 59

            # xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
            dialog_msg()
            hide_busy_dialog()
            # plugin.log.info(e)
            # traceback.print_exc()
    else:
        if id in ('1', '3'):  # if we were on 1st page, then the viewmode should remain to 58 as an error has occured and we haven't got any data for next screen
            mvl_view_mode = 58
        elif id in ('23', '104916', '112504', '32', '104917', '366042', '372395', '372396'):
            mvl_view_mode = 59

        #show error message
        dialog_msg()
        hide_busy_dialog()

