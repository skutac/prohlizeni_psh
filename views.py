# -*- coding: utf-8 -*-
import simplejson as json
import re
from itertools import *

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
   hesla = []
   topconcepts = Topconcepts.objects.all()
   for heslo in topconcepts:
       hesla.append(Hesla.objects.get(id_heslo=heslo.id_heslo))
   hesla.sort(key=lambda x: x.heslo)
   return render_to_response("index.html", {"hesla":hesla})

def index_en(request):
   """Returns main site"""
   hesla = []
   topconcepts = Topconcepts.objects.all()
   for heslo in topconcepts:
       hesla.append(Ekvivalence.objects.get(id_heslo=heslo.id_heslo))
   hesla.sort(key=lambda x: x.ekvivalent)
   return render_to_response("index_en.html", {"hesla":hesla})
            
#def getSubjectByHash(request, subjectID):
    #"""Return HTML representation of subject according to given PSH ID"""
    #try:
        #subject = open("".join([settings.ROOT, "/static/subjects/", subjectID, ".html"]), "r")
        #concept = subject.read()
        #subject.close()
        #return render_to_response("index.html", {'concept': concept})
    #except:
        #return render_to_response("index.html", {'concept': getConceptFromDB(subjectID)})
    
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
        
    
    return render_to_response("search_result.html", {"preferred": preferred, "nonpreferred":nonpreferred})
    # except Exception, e:
    #     return HttpResponse(str(e))
        

def bold(substring, text):
    """Boldify substring within a given text"""
    return re.sub(substring, "".join(["<b>", substring, "</b>"]), text)

def get_subject_id(request):
    """Get PSH ID for given text label (translate alternative label to preferred label)"""
    if request.GET["lang"] == 'cs':
        try:
            id = Hesla.objects.get(heslo=request.GET["input"]).id_heslo
        except:
            try:
                id = Varianta.objects.get(varianta=request.GET["input"], jazyk="cs").id_heslo.id_heslo
                
            except:
                id = "None"
    else:
        try:
            id = Ekvivalence.objects.get(ekvivalent=request.GET["input"]).id_heslo.id_heslo
        except:
            try:
                id = Varianta.objects.get(varianta=request.GET["input"], jazyk="en").id_heslo.id_heslo
            except:
                id = "None"
    return HttpResponse(id)

def get_concept(request, subject_id):
    """Interface for subject retrieval"""
    return render_to_response("concept.html", {"concept": get_concept_dict(subject_id, "cs")})

def get_concept_en(request, subject_id):
    """Interface for subject retrieval"""
    return render_to_response("concept_en.html", {"concept": get_concept_dict(subject_id, "en")})

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
        
        varianta = query_to_dicts("""SELECT varianta
                FROM varianta
                WHERE varianta.jazyk = 'en' AND varianta.id_heslo = '%s'""" %subject_id)

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
                
        varianta = query_to_dicts("""SELECT varianta
                FROM varianta
                WHERE varianta.jazyk = 'cs' AND varianta.id_heslo = '%s'""" %subject_id)

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
        heslo["nepreferovany"] = []

        for p in podrazeny:
                heslo["podrazeny"].append({"id_heslo":p["podrazeny"], "heslo":p["heslo"]})
        for p in pribuzny:
                heslo["pribuzny"].append({"id_heslo":p["pribuzny"], "heslo":p["heslo"]})
        for v in varianta:
                heslo["nepreferovany"].append(v["varianta"])
    else:
        heslo = ""
    return heslo


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

def getWikipediaLink(request):
    """Check for wikipedia link"""
    subjectID = request.POST["subjectID"]
    try:
        link = Vazbywikipedia.objects.get(id_heslo=subjectID)
        return HttpResponse("True")
    except Exception, e:
        return HttpResponse(str(e))