# -*- coding: utf-8 -*-
import simplejson as json
import re
from itertools import *
import urllib2, urllib

# from psh_manager_online import handler
# from psh_manager_online.psh.models import Hesla, Varianta, Ekvivalence, Hierarchie, Topconcepts, Pribuznost, Zkratka, Vazbywikipedia, SysNumber

from prohlizeni_psh.psh.models import Topconcepts, Hesla, Varianta, Ekvivalence

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.db import connection

def query_to_dicts(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return

def index(request):
   """Returns main site"""
   hesla = query_to_dicts("""SELECT topconcepts.id_heslo, hesla.heslo, psh_pocetzaznamu.pocet FROM topconcepts
                                JOIN hesla ON hesla.id_heslo = topconcepts.id_heslo
                                JOIN psh_pocetzaznamu ON psh_pocetzaznamu.id_heslo = topconcepts.id_heslo""")
   hesla = list(hesla)
   hesla = normalize_counts(hesla)
   hesla.sort(key=lambda x: x["heslo"])
   nav = {"lang":"cs" ,"search_label": "Vyhledávání", "english":"inactive", "czech":"active"}
   return render_to_response("index.html", {"hesla":hesla, "nav": nav})

def index_en(request):
   """Returns main site"""
   hesla = query_to_dicts("""SELECT topconcepts.id_heslo, ekvivalence.ekvivalent, psh_pocetzaznamu.pocet FROM topconcepts
                                JOIN ekvivalence ON ekvivalence.id_heslo = topconcepts.id_heslo
                                JOIN psh_pocetzaznamu ON psh_pocetzaznamu.id_heslo = topconcepts.id_heslo""")
   hesla = list(hesla)
   hesla = normalize_counts(hesla)
   hesla.sort(key=lambda x: x["ekvivalent"])
   nav = {"lang":"en" ,"search_label": "Search", "english":"active", "czech":"inactive"}
   return render_to_response("index_en.html", {"hesla":hesla, "nav":nav})
    
def suggest(request):
    """Return suggested labels according to given text input and language selector"""
    text_input = request.GET["input"]
    if request.GET["lang"] == "cs":
        hesla = Hesla.objects.filter(heslo__istartswith=text_input)
        alt = Varianta.objects.filter(varianta__istartswith=text_input, jazyk="cs")
        contains = Hesla.objects.filter(heslo__icontains=text_input).exclude(heslo__istartswith=text_input)
        alt_contains = Varianta.objects.filter(varianta__icontains=text_input, jazyk="cs").exclude(varianta__istartswith=text_input, jazyk="cs")
            
        seznam = [heslo.heslo for heslo in hesla]
            
        for heslo in alt:
            seznam.append(heslo.varianta)
        seznam.sort()
            
        seznam_contains = [heslo.heslo for heslo in contains]
        for heslo in alt_contains:
            seznam_contains.append(heslo.varianta)
        seznam_contains.sort()
        seznam.extend(seznam_contains)
    else:
        hesla = Ekvivalence.objects.filter(ekvivalent__istartswith=text_input)
        alt = Varianta.objects.filter(varianta__istartswith=text_input, jazyk="en")
        contains = Ekvivalence.objects.filter(ekvivalent__icontains=text_input).exclude(ekvivalent__istartswith=text_input)
        alt_contains = Varianta.objects.filter(varianta__icontains=text_input, jazyk="en").exclude(varianta__istartswith=text_input, jazyk="en")
            
        seznam = [heslo.ekvivalent for heslo in hesla]
            
        for heslo in alt:
            seznam.append(heslo.varianta)
        seznam.sort()
            
        seznam_contains = [heslo.ekvivalent for heslo in contains]
        for heslo in alt_contains:
            seznam_contains.append(heslo.varianta)
        seznam_contains.sort()
        seznam.extend(seznam_contains)
            
    return HttpResponse(json.dumps(seznam[0:60]), mimetype='application/json')

def search(request):
    """Return HTML site with search results to given text input and language selector"""
    term = request.GET['term']
    lang = request.GET['lang']

    preferred = []
    nonpreferred = []

    exact_match = get_exact_match(term,lang)
    if exact_match:
        if lang == "cs":
            return get_concept("", exact_match)
        else:
            return get_concept_en("", exact_match)

    if lang == "cs":
        subjects = Hesla.objects.filter(heslo__istartswith = term).order_by("heslo")
        subjects = [{"id_heslo": s.id_heslo, "heslo":bold(term,s.heslo)} for s in subjects]
        preferred.extend(subjects)

        subjects = Hesla.objects.filter(heslo__contains = term).order_by("heslo").exclude(heslo__istartswith=term)
        subjects = [{"id_heslo": s.id_heslo, "heslo":bold(term,s.heslo)} for s in subjects]
        preferred.extend(subjects)

        subjects = Varianta.objects.filter(varianta__istartswith = term, jazyk=lang).order_by("varianta")
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "varianta":bold(term, s.varianta), "heslo":bold(term, s.id_heslo.heslo)} for s in subjects]
        nonpreferred.extend(subjects)
                
        subjects = Varianta.objects.filter(varianta__contains = term, jazyk=lang).order_by("varianta").exclude(varianta__istartswith=term)
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "varianta":bold(term, s.varianta), "heslo":bold(term,s.id_heslo.heslo)} for s in subjects]
        nonpreferred.extend(subjects)
        nav = {"lang":"cs" ,"search_label": "Vyhledávání", "english":"inactive", "czech":"active"}
        return render_to_response("search_result.html", {"preferred": preferred, "nonpreferred":nonpreferred, "nav":nav})

    else:

        subjects = Ekvivalence.objects.filter(ekvivalent__istartswith = term).order_by("ekvivalent")
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "heslo":bold(term,s.ekvivalent)} for s in subjects]
        preferred.extend(subjects)

        subjects = Ekvivalence.objects.filter(ekvivalent__contains = term).order_by("ekvivalent").exclude(ekvivalent__istartswith=term)
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "heslo":bold(term,s.ekvivalent)} for s in subjects]
        preferred.extend(subjects)

        subjects = Varianta.objects.filter(varianta__istartswith = term, jazyk=lang).order_by("varianta")
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "varianta":bold(term, s.varianta), "heslo":bold(term, Ekvivalence.objects.get(id_heslo=s.id_heslo).ekvivalent )} for s in subjects]
        nonpreferred.extend(subjects)
                
        subjects = Varianta.objects.filter(varianta__contains = term, jazyk=lang).order_by("varianta").exclude(varianta__istartswith=term)
        subjects = [{"id_heslo": s.id_heslo.id_heslo, "varianta":bold(term, s.varianta), "heslo":bold(term, Ekvivalence.objects.get(id_heslo=s.id_heslo).ekvivalent )} for s in subjects]
        nonpreferred.extend(subjects)
        nav = {"lang":"en" ,"search_label": "Search", "english":"active", "czech":"inactive"}
        return render_to_response("search_result_en.html", {"preferred": preferred, "nonpreferred":nonpreferred, "nav":nav})
        
    # except Exception, e:
    #     return HttpResponse(str(e))
        

def bold(substring, text):
    """Boldify substring within a given text"""
    return re.sub(substring, "".join(["<b>", substring, "</b>"]), text)

def get_concept(request, subject_id):
    """Interface for subject retrieval"""
    nav = {"lang":"cs" ,"search_label": "Vyhledávání", "english":"inactive", "czech":"active"}
    return render_to_response("concept.html", {"concept": get_concept_dict(subject_id, "cs"), "nav": nav})

def get_concept_en(request, subject_id):
    """Interface for subject retrieval"""
    nav = {"lang":"en" ,"search_label": "Search", "english":"active", "czech":"inactive"}
    return render_to_response("concept_en.html", {"concept": get_concept_dict(subject_id, "en"), "nav": nav})

def get_concept_dict(subject_id, lang):

    if lang == "en":
        heslo = query_to_dicts("""SELECT ekvivalence.id_heslo, 
                ekvivalence.ekvivalent as heslo
                FROM ekvivalence
                WHERE ekvivalence.id_heslo = '%s'""" %subject_id)

        ekvivalent = query_to_dicts("""SELECT heslo as ekvivalent
                FROM hesla
                WHERE id_heslo = '%s'""" %subject_id)
    
        podrazeny = query_to_dicts("""SELECT podrazeny,
                ekvivalence.ekvivalent as heslo 
                FROM hierarchie
                LEFT JOIN ekvivalence ON ekvivalence.id_heslo = hierarchie.podrazeny
                WHERE nadrazeny = '%s'""" %subject_id)
    
        nadrazeny = query_to_dicts("""SELECT nadrazeny,
                ekvivalence.ekvivalent as heslo 
                FROM hierarchie
                LEFT JOIN ekvivalence ON ekvivalence.id_heslo = hierarchie.nadrazeny
                WHERE podrazeny = '%s'""" %subject_id)
    
        pribuzny = query_to_dicts("""SELECT pribuzny,
                ekvivalence.ekvivalent as heslo
                FROM pribuznost
                LEFT JOIN ekvivalence ON ekvivalence.id_heslo = pribuznost.pribuzny
                WHERE pribuznost.id_heslo = '%s'""" %subject_id)

        varianta = query_to_dicts("""SELECT varianta, jazyk
                FROM varianta
                WHERE varianta.id_heslo = '%s'""" %subject_id)

    elif lang == "cs":
        heslo = query_to_dicts("""SELECT hesla.id_heslo, 
                hesla.heslo 
                FROM hesla
                WHERE hesla.id_heslo = '%s'""" %subject_id)

        ekvivalent = query_to_dicts("""SELECT ekvivalent
                FROM ekvivalence
                WHERE id_heslo = '%s'""" %subject_id)
    
        podrazeny = query_to_dicts("""SELECT podrazeny,
                hesla.heslo 
                FROM hierarchie
                LEFT JOIN hesla ON hesla.id_heslo = hierarchie.podrazeny
                WHERE nadrazeny = '%s'""" %subject_id)
    
        nadrazeny = query_to_dicts("""SELECT nadrazeny,
                hesla.heslo 
                FROM hierarchie
                LEFT JOIN hesla ON hesla.id_heslo = hierarchie.nadrazeny
                WHERE podrazeny = '%s'""" %subject_id)
    
        pribuzny = query_to_dicts("""SELECT pribuzny,
                hesla.heslo 
                FROM pribuznost
                LEFT JOIN hesla ON hesla.id_heslo = pribuznost.pribuzny
                WHERE pribuznost.id_heslo = '%s'""" %subject_id)
                
        varianta = query_to_dicts("""SELECT varianta, jazyk
                FROM varianta
                WHERE varianta.id_heslo = '%s'""" %subject_id)

    else:
        heslo = ""
        
    heslo = list(heslo)
    if heslo:
        heslo = heslo[0]

        for n in nadrazeny:
            heslo["nadrazeny"] = [{"id_heslo":n["nadrazeny"], "heslo":n["heslo"]}]

        heslo["ekvivalent"] = list(ekvivalent)[0]["ekvivalent"]

        heslo["podrazeny"] = []
        heslo["pribuzny"] = []
        heslo["nepreferovany"] = {"en":[], "cs":[]}

        for p in podrazeny:
            count = query_to_dicts("""SELECT pocet FROM psh_pocetzaznamu WHERE id_heslo = '%s'"""%p["podrazeny"])
            count = int(list(count)[0]["pocet"])
            heslo["podrazeny"].append({"id_heslo":p["podrazeny"], "heslo":p["heslo"], "pocet":count})
        for p in pribuzny:
            heslo["pribuzny"].append({"id_heslo":p["pribuzny"], "heslo":p["heslo"]})
        for v in varianta:
            heslo["nepreferovany"][v["jazyk"]].append(v["varianta"])
    else:
        heslo = ""

    heslo["podrazeny"] = normalize_counts(heslo["podrazeny"])
    return heslo

def normalize_counts(hesla):
    counts = [h["pocet"] for h in hesla]
    counts = list(set(counts))
    counts.sort(key=lambda x: int(x))

    count2weight = {}
    for x in xrange(len(counts)):
        count2weight[counts[x]] = x

    for h in hesla:
        h["pocet"] = count2weight[h["pocet"]]

    return hesla


def get_exact_match(term, lang):
    if lang == "cs":
        hesla = [h.id_heslo for h in Hesla.objects.filter(heslo__contains=term)]
    else:
        hesla = [h.id_heslo.id_heslo for h in Ekvivalence.objects.filter(ekvivalent__contains=term)]
    
    hesla.extend([h.id_heslo.id_heslo for h in Varianta.objects.filter(varianta__contains=term, jazyk=lang)])

    if len(hesla) == 1:
        return hesla[0]
    else:
        return False


def get_concept_as_json(request, subject_id=None, lang="cs", callback=None):
        """Get concept form database according to its PSH ID"""
        try:
            if request.GET.get("subject_id"):
                subject_id = request.GET.get("subject_id")

            if request.GET.get("lang"):
                lang = request.GET.get("lang")
            
            if request.GET.get("callback"):
                callback = request.GET.get("callback")
        except:
            pass

        heslo = get_concept_dict(subject_id, lang)

        if callback:
            return HttpResponse("".join([callback, "(", json.dumps(heslo), ")"]))
        else:
            return HttpResponse(json.dumps(heslo), mimetype='application/json')

def get_czech_equivalent(subject):
    try:
        equivalent = query_to_dicts("""SELECT heslo FROM hesla
                                        JOIN ekvivalence on ekvivalence.id_heslo = hesla.id_heslo
                                        WHERE ekvivalence.ekvivalent = '%s'""" %subject)
        return list(equivalent)[0]["heslo"]
    except Exception, e:
        print str(e)

def get_library_records(request):
    try:
        subject = request.GET["subject"]
        lang = request.GET["lang"]

        if lang == "en":
            subject = get_czech_equivalent(subject)

        url = 'https://vufind.techlib.cz/vufind/Search/Results?lookfor="%s"&type=psh_facet&submit=Hledat'%subject
        url = url.encode("utf8")
        url = re.sub(" ", "+", url)
        records = []

        catalogue = urllib2.urlopen(url)
        catalogue_html = catalogue.read()

        if "nenalezlo žádné výsledky" in catalogue_html:
            records_html = ["<div id='catalogue_header'>Nebyl nalezen žádný záznam.  <a href='", url,"'>Přejít do katalogu NTK >></a></div>"]
            return HttpResponse("".join(records_html))

        record_count = re.search('class="yui-u first">(.*?)</div>', catalogue_html, re.S).group(1)
        record_count = [r for r in re.findall("<b>(.*?)</b>", record_count, re.S)][2].strip(" \n")

        catalogue_records = re.findall('record\d+">(.*?)getStatuses', catalogue_html, re.S)


        for record in catalogue_records:
            title = re.search('class="title">(.*?)</a', record, re.S).group(1).strip("/ ")
            link = re.search('resultItemLine1">.*?<a href="(.*?)"', record, re.S).group(1)
            author_match = re.search('resultItemLine2">.*?<a href="(.*?)">(.*?)<', record, re.S)
            
            if not "saveLink" in author_match.group(0):
                author_link = author_match.group(1)
                author = author_match.group(2).strip(" \n").split(",")
                if "1" in author[-1]:
                    author = author[:-1]
                author = ", ".join(author)
            else:
                author_link = ""
                author = ""

            published = re.search("Vydáno:</strong>(.*?)<", record, re.S)
            if published:
                published = published.group(1).strip(" \n")
            else:
                published = "-"

            records.append({"title":title, "link": link, "author":author, "author_link":author_link, "published":published})

        if lang == "en":
            records_html = ["<div id='catalogue_header'>Records 1 - ", str(len(records))," from ", record_count,", <a href='", url,"'>Go to the catalogue of NTK >></a></div>"]
        else:
            records_html = ["<div id='catalogue_header'>Záznamy 1 - ", str(len(records))," z celkem ", record_count,", <a href='", url,"'>Přejít do katalogu NTK >></a></div>"]
        records_html.append("<ul id='catalogue_records'>\n")
        for r in records:
            records_html.append("".join(['<li><a class="record_title" href="', r["link"],'">', r["title"],' (', r["published"],')</a>, <a class="author" href="', r["author_link"],'">', r["author"],'</a></li>\n']))

        records_html.append("</ul>\n")

        return HttpResponse("".join(records_html))
    except Exception, e:
        return HttpResponse(str(e))