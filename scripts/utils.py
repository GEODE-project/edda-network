
# importing all necessary modules
import lxml.etree as etree
import os
import re


def normalize(headword):
    names = {}
    
    det = "les|l'|le|la|los"
    prep = "des|del|de|du|d'"
    sep = "ou plûtôt|ou|et|autrement|&"
    type = "pays|port|pays|royaume|isle|ile|isola|île|iles|isla|lac|comté|détroit|sainte|saint|sant|san|mons|monts|nome|empire|alpes|golfe|nouvelle|canal|fort|fare|mer|état|terre|duché|grande|st"
    mot = "[\w\'\s-]"

    pattern0 = "^([\w\s-]*), c'est-à-dire,? ([\w\s-]*)"
    pattern1 = "^([\w\s]*),? ,?\(?("+det+")?\s?("+type+")+-?\s?("+prep+")?\)?$"
    #pattern0 = "^([\w\s]*),? ,?\(?(l'|le|la|les)\)?"
    #pattern1 = "^([\w\s]*),? ,?\(?([\w\s]*)\)?"

    pattern14 = "^(" + mot + "*),? ("+det+")?,?\s?("+sep+" |lac de |golfe, )?(en latin moderne|en latin|plus communément) ((" + det + ") )?(" + mot + "*)\s?("+sep+")?\s?("+det+")?\s?(" + mot + "*)?"

    pattern2 = "^(" + mot + "*),? ("+det+")?,?\s?("+sep+"|lac de|golfe)+ (en latin |plus communément )?(("+det+") )?(" + mot + "*)"

    pattern3 = "^(" + mot + "*), ("+det+")?,?\s?("+det+")?\s?(" + mot + "*), ("+det+")?,?\s?(("+det+") )?(" + mot + "*)"

    pattern4 = "^(" + mot + "*), ("+det+")?,?\s?("+sep+")+ (("+det+") )?(" + mot + "*), ("+det+")?,?\s?("+sep+")+ ("+det+")?\s?(" + mot + "*)"

    pattern5 = "^(" + mot + "*) \(?("+det+")+\)?,? ("+sep+")+ (("+det+") )?(" + mot + "*)"

    pattern9 = "^(" + mot + "*) ("+sep+")+ (" + mot + "*) ("+sep+")+ (" + mot + "*)"

    pattern12 = "^(" + mot + "*), (" + sep + ") (" + mot + "*), (" + mot + "*), (" + mot + "*)"

    pattern6 = "^(" + mot + "*) ("+det+")?,?\s?("+sep+")+ ("+det+")?\s?(" + mot + "*) ("+det+")?,?\s?("+sep+")+ (("+det+") )?(" + mot + "*)"

    pattern7 = "^(" + mot + "*),? ,?\(?("+det+")?\s?("+type+")?-?\s?("+prep+")?\)?, ("+sep+")?\s?(" + mot + "*)"

    pattern8 = "^(" + mot + "*), \(?("+ det+")?\)?$"

    pattern13 = "^(" + mot + "*) \((" + det + ")\)$"

    pattern10 = "^(" + mot + "*),? \("

    pattern15 = "^(" + mot + "*), "

    pattern11 = "^(" + mot + "*),? (" + det + "), (" + mot + "*) (" + sep + ") (" + mot + "*)"

    match = re.search(pattern14, headword, re.I)
    if match:
        #print('14 : ' + match.group(1) + ' + ' + match.group(7))
        names[match.group(1)] = []
        names[match.group(1)].append(match.group(7))

    else:
        match = re.search(pattern12, headword, re.I)
        if match:
            #print('12 : ' + match.group(1) + ' + ' + match.group(3))
            names[match.group(1)] = []
            names[match.group(1)].append(match.group(3))
            names[match.group(1)].append(match.group(4))
            names[match.group(1)].append(match.group(5))
        else:
            match = re.search(pattern11, headword, re.I)
            if match:
                #print('11 : ' + match.group(1) + ' + ' + match.group(3))
                names[match.group(1)] = []
                names[match.group(1)].append(match.group(2) + ' ' + match.group(1))
                names[match.group(1)].append(match.group(3))
                names[match.group(1)].append(match.group(5))
            else:
                match = re.search(pattern7, headword, re.I)
                if match:
                    #print('7 : ' + match.group(1) + ' + ' + match.group(6))
                    names[match.group(1)] = []
                    names[match.group(1)].append(match.group(6))
                else:
                    match = re.search(pattern9, headword, re.I)
                    if match:
                        #print('9 : ' + match.group(1) + ' + ' + match.group(3) + ' + ' + match.group(5))
                        names[match.group(1)] = []
                        names[match.group(1)].append(match.group(3))
                        names[match.group(1)].append(match.group(5))
                    else:
                        match = re.search(pattern6, headword, re.I)
                        if match:
                            #print('6 : ' + match.group(1) + ' + ' + match.group(5) + ' + ' + match.group(10))
                            names[match.group(1)] = []
                            names[match.group(1)].append(match.group(5))
                            names[match.group(1)].append(match.group(10))
                        else:
                            match = re.search(pattern4, headword, re.I)
                            if match:
                                #print('4 : ' + match.group(1) + ' + ' + match.group(6) + ' + ' + match.group(10))
                                names[match.group(1)] = []
                                names[match.group(1)].append(match.group(6))
                                names[match.group(1)].append(match.group(10))
                            else:
                                match = re.search(pattern5, headword, re.I)
                                if match:
                                    #print('5 : ' + match.group(1) + ' + ' + match.group(6))
                                    names[match.group(1)] = []
                                    names[match.group(1)].append(match.group(6))

                                else:
                                    match = re.search(pattern2, headword, re.I)
                                    if match:
                                        #print('2 : ' + match.group(1) + ' + ' + match.group(7))
                                        names[match.group(1)] = []
                                        names[match.group(1)].append(match.group(7))
                                    else:
                                        match = re.search(pattern3, headword, re.I)
                                        if match:
                                            # print('3 : ' + match.group(1) + ' + ' + match.group(4) + ' + ' + match.group(8))
                                            names[match.group(1)] = []
                                            names[match.group(1)].append(match.group(4))
                                            names[match.group(1)].append(match.group(8))
                                        else:

                                            match = re.search(pattern0, headword, re.I)
                                            if match:

                                                #print('0 : ' + match.group(1) + ' + ' + match.group(2))
                                                names[match.group(1)] = []
                                                names[match.group(1)].append(match.group(2))
                                            else:
                                                match = re.search(pattern8, headword, re.I)
                                                if match:
                                                    #print('8 : ' + match.group(1))
                                                    names[match.group(1)] = []
                                                    if match.group(2):
                                                        names[match.group(1)].append(match.group(2) + " " + match.group(1))
                                                else:
                                                    match = re.search(pattern13, headword, re.I)
                                                    if match:
                                                        #print('13 : ' + match.group(1))
                                                        names[match.group(1)] = []
                                                        if match.group(2):
                                                            names[match.group(1)].append(
                                                                match.group(2) + " " + match.group(1))
                                                    else:
                                                        match = re.search(pattern1, headword, re.I)
                                                        if match:
                                                            #print('1 : ' + match.group(1))
                                                            names[match.group(1)] = []
                                                            st = ""
                                                            if match.group(2):
                                                                st = match.group(2) + " "
                                                            if match.group(3):
                                                                st += match.group(3) + " "
                                                            if match.group(4):
                                                                st += match.group(4) + " "

                                                            names[match.group(1)].append(st + match.group(1))
                                                        else:

                                                            match = re.search(pattern10, headword, re.I)
                                                            if match:
                                                                #print('10 : ' + match.group(1))
                                                                names[match.group(1)] = []
                                                            else:
                                                                match = re.search(pattern15, headword, re.I)
                                                                if match:
                                                                    #print('15 : ' + match.group(1))
                                                                    names[match.group(1)] = []
                                                                else:
                                                                    #print('else : '+headword)
                                                                    names[headword] = []

    return names


def get_head(file_path, filename):

    try:
        tree = etree.parse(file_path+filename)
        root = tree.getroot()

        return root.find('./text/body/div1/index[@type="head"]').get('value')

    except etree.XMLSyntaxError as e:
        print(filename + ' : ' + str(e))
        return None


def write_files(content, output_path):

    if content is not None:
        with open(output_path + 'normHeadGeo_v20200509.csv', 'w') as fichier:
            fichier.write(content)


if __name__ == "__main__":

    input_path = '/Users/lmoncla/Documents/Data/Corpus/EDDA/articles_geographie/geo_tei/'
    output_path = '/Users/lmoncla/Documents/Data/Corpus/EDDA/articles_geographie/'

    content = ''

    #headword = normalize('RATZEBOURG, ou RAZEBOURG')

    content = 'filename;head;normalized name; alt names;'

    for doc in os.listdir(input_path):
        file_id = doc[:-4]
        #print('artcile ' + file_id)
        extension = doc[-4:]

        if extension == '.tei':
            head = get_head(input_path, doc)

            if head is not None:

                content += '\n' + file_id + ';' + head + ';'

                headword = normalize(head)
                print(headword)
                for name, altNames in headword.items():
                    content += name + ';'

                    if altNames:
                        for val in altNames:
                            content += val + ';'



    print(content)
    write_files(content, output_path)


print('done!')