# importing all necessary modules
import lxml.etree as etree
import os
import operator
import re
import networkx as nx
import pymysql.cursors
from utils import normalize


def create_nodes_with_geocoding(file_path, filename, number, cursor):

    try:
        tree = etree.parse(file_path + filename)
        root = tree.getroot()

        for div1 in root.findall('./text/body/div1'):

            volume = div1.get('vol')
            # <index type="head"
            for index in root.findall(".//index[@type='head']"):
                head_value = index.get('value')

            for index in root.findall(".//index[@type='normclass']"):
                normclass = index.get('value')

            for index in root.findall(".//index[@type='author']"):
                author = index.get('value')

            ''' on normalise et stock le noeud dans un dictionnaire '''

            k = norm_headwords(head_value.lower())

            alt_names = ', '.join(d_headwords[k])

            #nbwords = sum(1 for _ in div1.findall('.//w'))
            nbwords = 0
            for w in div1.findall('.//w'):
                # sauf PUN et SEN
                if w.get("type") != 'PUN' and w.get("type") != 'SEN':
                    nbwords += 1

            nbEN = len(div1.findall(".//name"))
            nbNameEDDA = len(div1.findall(".//name[@type='place'][@subtype='edda']"))
            nbPers = len(div1.findall(".//name[@type='person']"))

            nbENE = len(div1.findall(".//rs[@type='ene']/rs[@subtype='ene']"))
            nbENEPlace = len(div1.findall(".//rs[@type='ene']/rs[@type='place'][@subtype='ene']"))
            nbENEPers = len(div1.findall(".//rs[@type='ene']/rs[@type='person'][@subtype='ene']"))

            nbENEDDAGeocoded = len(div1.findall(".//name[@type='place'][@subtype='edda']/location"))
            nbENGeocoded = len(div1.findall(".//name[@type='place']/location"))

            latlongValue = []
            latlong = False
            for ll in div1.findall(".//rs[@type='place'][@subtype='latlong']/geo"):
                latlong = True

                latlongValue.append(ll.text)

            w1 = ''
            w2 = ''
            # first word : //term[@type='articleClass']/following::w[1]
            for w in div1.xpath(".//rs[@type='articleClass']/following::w[1]"):
                w1 = w.text.lower()

            for w in div1.xpath(".//rs[@type='articleClass']/following::w[2]"):
                w2 = w.text.lower()

            type_geo = ''
            if w1 != '':
                if w1 == 'ville' or w1 == 'village' or w1 == 'capitale' or w1 == 'bourgade' or w1 == 'bourg' or w1 == 'cité' or w1 == 'municipe':
                    w1 = 'ville'

                if w1 == 'pays' or w1 == 'province' or w1 == 'royaume' or w1 == 'contrée' or w1 == 'gouvernement' or w1 == 'canton' \
                        or w1 == 'principauté' or w1 == 'district' or w1 == 'duché':
                    w1 = 'pays'

                if w1 == 'fleuve' or w1 == 'riviere' or w1 == 'rivière' or w1 == 'lac' or w1 == 'marais' or w1 == 'golfe' or w1 == 'baie':
                    w1 = 'hydronyme'

                if w1 == 'île' or w2 == 'îles' or w2 == 'isle':
                    w1 = 'île'

                if w1 == 'ville' or w1 == 'pays' or w1 == 'hydronyme' or w1 == 'montagne' or w1 == 'ruine' or w1 == 'île':
                    type_geo = w1

            if w2 != '':
                if w2 == 'ville' or w2 == 'village' or w2 == 'capitale' or w2 == 'bourgade' or w2 == 'bourg' or w2 == 'cité' or w2 == 'municipe':
                    w2 = 'ville'

                if w2 == 'pays' or w2 == 'province' or w2 == 'royaume' or w2 == 'contrée' or w2 == 'gouvernement' or w2 == 'canton' \
                        or w2 == 'principauté' or w2 == 'district' or w2 == 'duché':
                    w2 = 'pays'

                if w2 == 'fleuve' or w2 == 'riviere' or w2 == 'rivière' or w2 == 'lac' or w2 == 'marais' or w2 == 'golfe' or w2 == 'baie':
                    w2 = 'hydronyme'

                if w2 == 'île' or w2 == 'îles' or w2 == 'isle':
                    w2 = 'île'

                if w2 == 'ville' or w2 == 'pays' or w2 == 'hydronyme' or w2 == 'montagne' or w2 == 'ruine' or w2 == 'île':
                    type_geo = w2

            #  print('nb words: ' + str(nbwords))
            #  print('nb en: ' + str(nb_en))
            #  print('nb ene: ' + str(nb_ene))
            #  print('nb en place: ' + str(nb_en_place))
            #  print('nb en person: ' + str(nb_en_person))
            #  print('nb type_equal: ' + str(type_equal))
            #  print('nb type_different: ' + str(type_different))
            #  print('latlong: ' + str(latlong))
            lat = ''
            long = ''
            lat_altNames = ''
            long_altNames = ''
            ''' GEOCODING '''
            query = 'SELECT wiki_title, lat, lon, type, country, region FROM location WHERE wiki_title="' + k + '"'
            cursor.execute(query)
            res = ''
            records = cursor.fetchall()
            for i, rec in enumerate(records):
                res += str(rec)
                if i == 0:
                    lat = float(rec[1])
                    long = float(rec[2])

            ''' GEOCODING alternate names'''
            query = 'SELECT wiki_title, lat, lon, type, country, region FROM location JOIN altname ' \
                    'ON altname.main_id = location.id WHERE altname = "' + k + '"'
            cursor.execute(query)
            res_altnames = ''
            records_altnames = cursor.fetchall()
            for i, rec in enumerate(records_altnames):
                res_altnames += str(rec)
                if i == 0:
                    lat_altNames = float(rec[1])
                    long_altNames = float(rec[2])

            print('name ' + k + ' - ' + str(len(records)) + ' - ' + str(res))

            if len(latlongValue) > 0:
                latlong_val = '; '.join(latlongValue)
            else:
                latlong_val = ''

            ''' Add node '''
            G.add_node(k, filename=filename, latitude=lat, longitude=long, author=author, normclass=normclass, volume=volume, number=number,
                       alt_names=alt_names, nb_wrd=nbwords, nb_en=nbEN, nb_ene=nbENE, nb_placeEDDA=nbNameEDDA,
                       nb_ene_place=nbENEPlace, nb_ENGeocoded=nbENGeocoded, nbENEDDAGeocoded=nbENEDDAGeocoded,
                       nb_en_pers=nbPers, nb_enePerson=nbENEPers, typegeo=type_geo, latlong=latlong,
                       latlong_value=latlong_val, nbWikiRecords=len(records), geocoding=res,
                       nbWikiRecords_altNames=len(records_altnames), geocoding_altNames=res_altnames, lat_altNames=lat_altNames,
                       long_altNames=long_altNames)

            print('Create node : ' + k + ' = ' + str(d_headwords[k]))

    except etree.XMLSyntaxError as e:
        print('Error : ' + str(e))



def create_nodes(file_path, filename, number):

    try:
        tree = etree.parse(file_path + filename)
        root = tree.getroot()

        for div1 in root.findall('./text/body/div1'):

            volume = div1.get('vol')
            # <index type="head"
            for index in root.findall(".//index[@type='head']"):
                head_value = index.get('value')

            for index in root.findall(".//index[@type='normclass']"):
                normclass = index.get('value')

            for index in root.findall(".//index[@type='author']"):
                author = index.get('value')

            ''' on normalise et stock le noeud dans un dictionnaire '''

            k = norm_headwords(head_value.lower())

            alt_names = ', '.join(d_headwords[k])

            #nbwords = sum(1 for _ in div1.findall('.//w'))
            nbwords = 0
            for w in div1.findall('.//w'):
                # sauf PUN et SEN
                if w.get("type") != 'PUN' and w.get("type") != 'SEN':
                    nbwords += 1

            nbEN = len(div1.findall(".//name"))
            nbNameEDDA = len(div1.findall(".//name[@type='place'][@subtype='edda']"))
            nbPers = len(div1.findall(".//name[@type='person']"))

            nbENE = len(div1.findall(".//rs[@type='ene']/rs[@subtype='ene']"))
            nbENEPlace = len(div1.findall(".//rs[@type='ene']/rs[@type='place'][@subtype='ene']"))
            nbENEPers = len(div1.findall(".//rs[@type='ene']/rs[@type='person'][@subtype='ene']"))

            nbENEDDAGeocoded = len(div1.findall(".//name[@type='place'][@subtype='edda']/location"))
            nbENGeocoded = len(div1.findall(".//name[@type='place']/location"))

            latlongValue = []
            latlong = False
            for ll in div1.findall(".//rs[@type='place'][@subtype='latlong']/geo"):
                latlong = True

                latlongValue.append(ll.text)

            w1 = ''
            w2 = ''
            # first word : //term[@type='articleClass']/following::w[1]
            for w in div1.xpath(".//rs[@type='articleClass']/following::w[1]"):
                w1 = w.text.lower()

            for w in div1.xpath(".//rs[@type='articleClass']/following::w[2]"):
                w2 = w.text.lower()

            type_geo = ''
            if w1 != '':
                if w1 == 'ville' or w1 == 'village' or w1 == 'capitale' or w1 == 'bourgade' or w1 == 'bourg' or w1 == 'cité' or w1 == 'municipe':
                    w1 = 'ville'

                if w1 == 'pays' or w1 == 'province' or w1 == 'royaume' or w1 == 'contrée' or w1 == 'gouvernement' or w1 == 'canton' \
                        or w1 == 'principauté' or w1 == 'district' or w1 == 'duché':
                    w1 = 'pays'

                if w1 == 'fleuve' or w1 == 'riviere' or w1 == 'rivière' or w1 == 'lac' or w1 == 'marais' or w1 == 'golfe' or w1 == 'baie':
                    w1 = 'hydronyme'

                if w1 == 'île' or w2 == 'îles' or w2 == 'isle':
                    w1 = 'île'

                if w1 == 'ville' or w1 == 'pays' or w1 == 'hydronyme' or w1 == 'montagne' or w1 == 'ruine' or w1 == 'île':
                    type_geo = w1

            if w2 != '':
                if w2 == 'ville' or w2 == 'village' or w2 == 'capitale' or w2 == 'bourgade' or w2 == 'bourg' or w2 == 'cité' or w2 == 'municipe':
                    w2 = 'ville'

                if w2 == 'pays' or w2 == 'province' or w2 == 'royaume' or w2 == 'contrée' or w2 == 'gouvernement' or w2 == 'canton' \
                        or w2 == 'principauté' or w2 == 'district' or w2 == 'duché':
                    w2 = 'pays'

                if w2 == 'fleuve' or w2 == 'riviere' or w2 == 'rivière' or w2 == 'lac' or w2 == 'marais' or w2 == 'golfe' or w2 == 'baie':
                    w2 = 'hydronyme'

                if w2 == 'île' or w2 == 'îles' or w2 == 'isle':
                    w2 = 'île'

                if w2 == 'ville' or w2 == 'pays' or w2 == 'hydronyme' or w2 == 'montagne' or w2 == 'ruine' or w2 == 'île':
                    type_geo = w2

            #  print('nb words: ' + str(nbwords))
            #  print('nb en: ' + str(nb_en))
            #  print('nb ene: ' + str(nb_ene))
            #  print('nb en place: ' + str(nb_en_place))
            #  print('nb en person: ' + str(nb_en_person))
            #  print('nb type_equal: ' + str(type_equal))
            #  print('nb type_different: ' + str(type_different))
            #  print('latlong: ' + str(latlong))
            
            if len(latlongValue) > 0:
                latlong_val = '; '.join(latlongValue)
            else:
                latlong_val = ''

            ''' Add node '''
            G.add_node(k, filename=filename, author=author, normclass=normclass, volume=volume, number=number,
                       alt_names=alt_names, nb_wrd=nbwords, nb_en=nbEN, nb_ene=nbENE, nb_placeEDDA=nbNameEDDA,
                       nb_ene_place=nbENEPlace, nb_ENGeocoded=nbENGeocoded, nbENEDDAGeocoded=nbENEDDAGeocoded,
                       nb_en_pers=nbPers, nb_enePerson=nbENEPers, typegeo=type_geo, latlong=latlong, latlong_value=latlong_val,)

            print('Create node : ' + k + ' = ' + str(d_headwords[k]))

    except etree.XMLSyntaxError as e:
        print('Error : ' + str(e))



def get_nb_typeEqual(element):
    nb = 0
    for rs in element.findall(".//rs[@subtype='ene']"):
        ene_type = rs.get('type')
        en = rs.find(".//rs")
        if en is not None:

            if ene_type == en.get('type'):
                #  print(ene_type + ' == ' + en.get('type'))
                nb += 1

    return nb


def get_nb_typeDifferent(element):
    nb = 0
    for rs in element.findall(".//rs[@subtype='ene']"):
        ene_type = rs.get('type')
        en = rs.find(".//rs")
        if en is not None:

            if ene_type != en.get('type'):
                #  print(ene_type + ' != ' + en.get('type'))
                nb += 1

    return nb


def norm_headwords(head_value):

    '''
    if ', ou ' in head_value:
        
        for temp in head_value.split(', ou '):
            if ', ' in temp:
                k = temp.split(', ')[0]
                for temp2 in temp.split(', '):
                    d.append(temp2)
            else:
                k = temp
                d.append(temp)

    elif ', et' in head_value:
        d = []
        for temp in head_value.split(', et '):
            if ', ' in temp:
                k = temp.split(', ')[0]
                for temp2 in temp.split(', '):
                    d.append(temp2)
            else:
                k = temp
                d.append(temp)

    elif 'et' in head_value:
        d = []
        k = head_value.split(' et ')[0]
        for temp in head_value.split(' et '):
            d.append(temp)

    elif 'ou' in head_value:
        d = []
        k = head_value.split(' ou ')[0]
        for temp in head_value.split(' ou '):
            d.append(temp)

    elif ', ' in head_value:
        d = []

        temp = head_value.split(', ')
        k = temp[0]
        d.append(temp[0])
        d.append(temp[1] + ' ' + temp[0])

    else:
        d = []
        k = head_value
        d.append(head_value)
    '''

    headword = normalize(head_value.lower())

    for name, altNames in headword.items():
        k = name
        d_headwords[name] = []
        d_headwords[name].append(name)

        if altNames:
            for val in altNames:
                d_headwords[name].append(val)

    return k


def key_headwords(head_value):

    '''
    if ', ou ' in head_value:

        for temp in head_value.split(', ou '):
            if ', ' in temp:
                k = temp.split(', ')[0]
            else:
                k = temp

    elif ', et' in head_value:

        for temp in head_value.split(', et '):
            if ', ' in temp:
                k = temp.split(', ')[0]
            else:
                k = temp

    elif 'et' in head_value:
        k = head_value.split(' et ')[0]

    elif 'ou' in head_value:
        k = head_value.split(' ou ')[0]

    elif ', ' in head_value:
        temp = head_value.split(', ')
        k = temp[0]

    else:
        k = head_value
    '''

    headword = normalize(head_value.lower())

    return next(iter(headword))


def create_edges(file_path, filename, number):
    try:

        tree = etree.parse(file_path+filename)
        root = tree.getroot()

        for div1 in root.findall('./text/body/div1'):

            # <index type="head"
            for index in root.findall(".//index[@type='head']"):
                head_value = index.get('value').lower()

            #  print('head_value : ' + head_value)

            key = key_headwords(head_value)  #  on récupère la clé dans le dictionnaire des headwords qui correspond à la valeur du head

            #  print(key)

            #  print(d_headwords[key])

            for name in div1.findall('.//name'):

                # print(name.tag)
                token = get_w_content(name).lower()

                if token == 'grande bretagne' or token == 'grande - bretagne' or token == 'grande-bretagne':
                    token = 'bretagne (grande)'
                    print('token = bretagne (grande)')
                    #time.sleep(5)

                for c, v in d_headwords.items():
                    if token in v:
                        if key != c:
                            number_node = G.nodes[key]['number']
                            # check the number of article of the corresponding node
                            if number == number_node:
                                print("Create edge : " + key + ' -> ' + c)
                                G.add_edge(key, c)

    except etree.XMLSyntaxError as e:
        print('Error : ' + str(e))


def save_edges_as_csv(outputFile, separator, edges):
    content = ''
    for e in edges:
        content += str(e[0]) + separator + str(e[1]+'\n')

    if content is not None:
        with open(outputFile, 'w') as fichier:
            fichier.write(content)


def save_nodes_as_csv(outputFile, separator, nodes):

    content = 'filename' + separator + 'headword' + separator + 'normclass' + separator + 'author' + separator \
              + 'volume' + separator + 'number' + separator + 'alt names' + separator + 'nb wrd' + separator \
              + 'nb EN' + separator + 'nb ENE' + separator \
              + 'nb place EDDA' + separator + 'nb ENE Place' + separator + 'nb EN Geocoded' + separator \
              + 'nb ENE Geocoded' + separator + 'nb EN Person' + separator + 'nb ENE Person' + separator \
              + 'typegeo' + separator + 'latlong' + separator + 'latlong value' + separator \
              + 'in_degree' + separator + 'out_degree' + separator + '\n'
              #+ 'nb wiki records' + separator + 'geocoding' + separator + 'lat' + separator + 'long' + separator \
              #+ 'nbWikiRecords_altNames' + separator + 'geocoding altnames' + separator + 'lat_altNames' + separator \
              #+ 'long_altNames' + separator 

    #  G.add_node(k, author=author, normclass=normclass, volume=volume, nb_wrd=nbwords, nb_en=nb_en, nb_ene=nb_ene,
    #                        nb_enPlace=nb_en_place, nb_enPerson=nb_en_person, nb_type_equal=type_equal,
    #                        nb_type_different=type_different, latlong=latlong)

    for n in nodes:
        content += G.nodes[n]['filename'] + separator + str(n) + separator + G.nodes[n]['normclass'] + separator + G.nodes[n]['author'] \
                   + separator + G.nodes[n]['volume'] + separator + G.nodes[n]['number'] + separator + G.nodes[n]['alt_names'] + separator + str(G.nodes[n]['nb_wrd']) \
                   + separator + str(G.nodes[n]['nb_en']) + separator + str(G.nodes[n]['nb_ene']) + separator + str(G.nodes[n]['nb_placeEDDA']) \
                   + separator + str(G.nodes[n]['nb_ene_place']) + separator + str(G.nodes[n]['nb_ENGeocoded']) + separator + str(G.nodes[n]['nbENEDDAGeocoded']) \
                   + separator + str(G.nodes[n]['nb_en_pers']) + separator + str(G.nodes[n]['nb_enePerson']) \
                   + separator + str(G.nodes[n]['typegeo']) + separator + str(G.nodes[n]['latlong']) \
                   + separator + str(G.nodes[n]['latlong_value']) \
                   + separator + str(G.in_degree(n)) + separator + str(G.out_degree(n)) + separator + '\n'
                   #+ separator + str(G.nodes[n]['nbWikiRecords']) \
                   #+ separator + str(G.nodes[n]['geocoding']) + separator + str(G.nodes[n]['latitude']) + separator + str(G.nodes[n]['longitude']) \
                   #+ separator + str(G.nodes[n]['nbWikiRecords_altNames']) + separator + str(G.nodes[n]['geocoding_altNames']) \
                   #+ separator + str(G.nodes[n]['lat_altNames']) + separator + str(G.nodes[n]['long_altNames']) \
                  

    if content is not None:
        with open(outputFile, 'w') as fichier:
            fichier.write(content)


def save_as_json(outputFile, G):

    cpt = 0
    content = '{'
    content += '"nodes" : ['
    for n in G.nodes:
        if cpt > 0:
            content += ','
        cpt += 1

        print(G.node[n])

        content += '{'
        content += '"id" : "'+str(n)+'",'
        content += '"normclass" : "' + G.node[n]['normclass'] + '",'
        content += '"author" : "' + G.node[n]['author'] + '",'
        content += '"volume" : "' + G.node[n]['volume'] + '"'
        content += '}'

    content += '],'
    content += '"links" : ['

    cpt = 0
    for e in G.edges:
        if cpt > 0:
            content += ','
        cpt += 1

        content += '{'
        content += '"source" : "' + str(e[0]) + '",'
        content += '"target" : "' + str(e[1]) + '",'
        content += '"value" : 1'
        content += '}'

    content += ']'
    content += '}'

    if content is not None:
        with open(outputFile, 'w') as fichier:
            fichier.write(content)


def get_w_content(element):
    content = ""
    for w in element.findall('.//w'):
        content += w.text + " "

    return content.strip()


if __name__ == "__main__":

    input_path = '/Users/lmoncla/Documents/Data/Corpus/EDDA/articles_geographie/perdido-22.06/'
    # input_path = '/Users/lmoncla/Documents/Data/Corpus/EDDA/test/'
    output_path = './output/'
    output_sync = output_path # '/Users/lmoncla/ownCloud/Recherche/Projets/2019 - MSH GéoDISCO/Data/output/'

    outputSuffix = 'v20221003'

    createNetwork = True

    if createNetwork:

        d_headwords = {}
        headwords = []

        G = nx.DiGraph()


         # create nodes
        for doc in os.listdir(input_path):
            file_id = doc[:-4]
            # print('artcile ' + file_id)
            extension = doc[-4:]

            if extension == '.xml':
                m = re.match("\w+-(\d+)", file_id)
                number = m.groups()[0]
                create_nodes(input_path, doc, number)

        '''
        # Connect to the database for geocoding
        connection = pymysql.connect(
            host="localhost",
            user="lmoncla",
            passwd="lentropie",
            database="wikiGazetteer"
        )
        try:
            with connection.cursor() as cursor:

                # create nodes
                for doc in os.listdir(input_path):
                    file_id = doc[:-4]
                    # print('artcile ' + file_id)
                    extension = doc[-4:]

                    if extension == '.xml':
                        m = re.match("\w+-(\d+)", file_id)
                        number = m.groups()[0]
                        create_nodes(input_path, doc, number, cursor)
        finally:
            connection.close()
        '''
        # create edges
        for doc in os.listdir(input_path):
            file_id = doc[:-4]
            # print('artcile ' + file_id)
            extension = doc[-4:]

            if extension == '.xml':
                m = re.match("\w+-(\d+)", file_id)
                number = m.groups()[0]
                create_edges(input_path, doc, number)

        # save graph
        nx.write_gexf(G, output_path + 'network-'+outputSuffix+'.gexf')
    else:
        # load graph
        G = nx.read_gexf(output_path + 'network-'+outputSuffix+'.gexf')

    # print('filename node : ' + str(G.node['egypte']['filename']))

    #print('nodes : ' + str(list(G.nodes(data=True))))
    #print('edges : ' + str(list(G.edges)))


    '''
    egoG = nx.ego_graph(G, 'acre', radius=2, undirected=True)

    print('nodes ego : ' + str(list(egoG.nodes(data=True))))

    centralityG = nx.betweenness_centrality(egoG)
    print('nodes centralityG : ' + str(centralityG))

    print(max(centralityG.items(), key=operator.itemgetter(1))[0])
    '''


    # save_edges_as_csv(output_path + 'edges-'+outputSuffix+'.csv', ';', G.edges)
    save_nodes_as_csv(output_path + 'nodes-' + outputSuffix + '.tsv', '\t', G.nodes)



    #save_as_json(output_path + 'graph-'+outputSuffix+'.json', G)


    print('done!')
