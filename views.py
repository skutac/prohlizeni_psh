# -*- coding: utf-8 -*-
import simplejson as json
import re

from psh_manager_online import handler
from psh_manager_online.psh.models import Hesla, Varianta, Ekvivalence, Hierarchie, Topconcepts, Pribuznost, Zkratka, Vazbywikipedia, SysNumber

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings

def index(request):
   """Returns main site"""
   hesla = []
   topconcepts = Topconcepts.objects.all()
   for heslo in topconcepts:
       hesla.append(Hesla.objects.get(id_heslo=heslo.id_heslo))
   hesla.sort(key=lambda x: x.heslo)
   return render_to_response("index.html", {"hesla":hesla})
            
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
    try:
        if request.POST["en"] == "inactive":
            hesla = Hesla.objects.filter(heslo__istartswith=request.POST["input"])
            alt = Varianta.objects.filter(varianta__istartswith=request.POST["input"], jazyk="cs")
            contains = Hesla.objects.filter(heslo__icontains=request.POST["input"]).exclude(heslo__istartswith=request.POST["input"])
            alt_contains = Varianta.objects.filter(varianta__icontains=request.POST["input"], jazyk="cs").exclude(varianta__istartswith=request.POST["input"], jazyk="cs")
            
            seznam = [heslo.heslo for heslo in hesla]
            
            for heslo in alt:
                seznam.append(heslo.varianta)
            seznam.sort()
            
            seznam_contains = [heslo.heslo for heslo in contains]
            for heslo in alt_contains:
                seznam_contains.append(heslo.varianta)
            seznam_contains.sort()
            seznam.extend(seznam_contains)
            
            return HttpResponse(json.dumps(seznam[0:60]), mimetype='application/json')
        else:
            hesla = Ekvivalence.objects.filter(ekvivalent__istartswith=request.POST["input"])
            alt = Varianta.objects.filter(varianta__istartswith=request.POST["input"], jazyk="en")
            contains = Ekvivalence.objects.filter(ekvivalent__icontains=request.POST["input"]).exclude(ekvivalent__istartswith=request.POST["input"])
            alt_contains = Varianta.objects.filter(varianta__icontains=request.POST["input"], jazyk="en").exclude(varianta__istartswith=request.POST["input"], jazyk="en")
            
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
            
    except Exception, e:
        return HttpResponse(str(e))

def getSearchResult(request):
    """Return HTML site with search results to given text input and language selector"""
    try:
        substring = request.POST['substring']
        english = request.POST['english']
        result = []
        result.append("".join([u"<h3>Výsledek hledání pro text <i>'", substring, "'</i>:</h3>"]))
        result.append("<ul id='searchResult'>")
        if english == "inactive":
            subjects = Hesla.objects.filter(heslo__istartswith = substring).order_by("heslo")
            result.extend(["".join(["<li itemid='", subject.id_heslo ,"' class='clickable'>", bold(substring, subject.heslo), "</li>"]) for subject in subjects])
            
            subjects = Varianta.objects.filter(varianta__istartswith = substring, jazyk="cs").order_by("varianta")
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.varianta), " (<i>", subject.id_heslo.heslo, "</i>)</li>"]) for subject in subjects])
            
            subjects = Hesla.objects.filter(heslo__contains = substring).order_by("heslo").exclude(heslo__istartswith=substring)
            result.extend(["".join(["<li itemid='", subject.id_heslo ,"' class='clickable'>", bold(substring, subject.heslo), "</li>"]) for subject in subjects])
            
            subjects = Varianta.objects.filter(varianta__contains = substring, jazyk="cs").order_by("varianta").exclude(varianta__istartswith=substring)
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.varianta), " (<i>", subject.id_heslo.heslo, "</i>)</li>"]) for subject in subjects])
            
        else:
            subjects = Ekvivalence.objects.filter(ekvivalent__istartswith = substring).order_by("ekvivalent")
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.ekvivalent), "</li>"]) for subject in subjects])
            
            subjects = Varianta.objects.filter(varianta__istartswith = substring, jazyk="en").order_by("varianta")
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.varianta), " (<i>", Ekvivalence.objects.get(id_heslo=subject.id_heslo.id_heslo).ekvivalent, "</i>)</li>"]) for subject in subjects])
            
            subjects = Ekvivalence.objects.filter(ekvivalent__contains = substring).order_by("ekvivalent").exclude(ekvivalent__istartswith=substring)
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.ekvivalent), "</li>"]) for subject in subjects])
            
            subjects = Varianta.objects.filter(varianta__contains = substring, jazyk="en").order_by("varianta").exclude(varianta__istartswith=substring)
            result.extend(["".join(["<li itemid='", subject.id_heslo.id_heslo ,"' class='clickable'>", bold(substring, subject.varianta), " (<i>", Ekvivalence.objects.get(id_heslo=subject.id_heslo.id_heslo).ekvivalent, "</i>)</li>"]) for subject in subjects])
            
        result.append("</ul>")
    
        return HttpResponse("".join(result))
    except Exception, e:
        return HttpResponse(str(e))
        

def bold(substring, text):
    """Boldify substring within a given text"""
    return re.sub(substring, "".join(["<b>", substring, "</b>"]), text)

def getID(request):
    """Get PSH ID for given text label (translate alternative label to preferred label)"""
    if request.POST["en"] == 'inactive':
        try:
            id = Hesla.objects.get(heslo=request.POST["input"]).id_heslo
        except:
            try:
                id = Varianta.objects.get(varianta=request.POST["input"], jazyk="cs").id_heslo.id_heslo
                
            except:
                id = "None"
    else:
        try:
            id = Ekvivalence.objects.get(ekvivalent=request.POST["input"]).id_heslo.id_heslo
        except:
            try:
                id = Varianta.objects.get(varianta=request.POST["input"], jazyk="en").id_heslo.id_heslo
            except:
                id = "None"
    return HttpResponse(id)

def get_concept(request, subject_id):
    """Interface for subject retrieval"""
    hesla = []
    try:
        current_subjects = Hierarchie.objects.filter(nadrazeny=subject_id)
        for heslo in current_subjects:
            hesla.append(Hesla.objects.get(id_heslo=heslo.podrazeny))
        hesla.sort(key=lambda x: x.heslo)
        
        #return HttpResponse(getConceptAsJSON(request.POST["subjectID"]))
        return render_to_response("index.html", {"hesla":hesla})
    except Exception, e:
        return render_to_response("404.html", {})

def getConceptAsJSON(subjectID):
        """Get concept form database according to its PSH ID"""
        none = "<li>-</li>"
        try:
            heslo = Hesla.objects.get(id_heslo=subjectID)
            titleCS = heslo.heslo
            acronym = Zkratka.objects.get(id_heslo=subjectID).zkratka
            titleEN = Ekvivalence.objects.get(id_heslo=subjectID).ekvivalent
            sysno = SysNumber.objects.get(id_heslo=subjectID).sysnumber
            
            narrowerID = Hierarchie.objects.filter(nadrazeny=subjectID)
            narrowerObj = [Hesla.objects.get(id_heslo=narrow.podrazeny) for narrow in narrowerID]
            narrowerObj.sort(key=lambda subject: subject.heslo.lower())
            narrower = []
            if len(narrowerObj) > 0:
                for narrow in narrowerObj:
                        narrower.append(u"<li itemid='%s' class='clickable'>%s</li>"%(narrow.id_heslo, narrow.heslo))
            else:
                narrower = none
                
            try:
                broader = Hierarchie.objects.get(podrazeny=subjectID)
                broader = u"<li itemid='%s' class='clickable'>%s</li>"%(broader.nadrazeny ,Hesla.objects.get(id_heslo=broader.nadrazeny).heslo)
            except:
                broader = none
            
            variantaCS = Varianta.objects.filter(id_heslo=subjectID, jazyk="cs").order_by("varianta")
            nonprefCS = []
            if len(variantaCS) > 0:
                for var in variantaCS:
                    nonprefCS.append("".join(["<li>", var.varianta, "</li>"]))
            else:
                nonprefCS = none
    
            variantaEN = Varianta.objects.filter(id_heslo=subjectID, jazyk="en").order_by("varianta")
            nonprefEN = []
            if len(variantaEN) > 0:
                for var in variantaEN:
                    nonprefEN.append("".join(["<li>", var.varianta, "</li>"]))
            else:
                nonprefEN = none
            
            relatedID = Pribuznost.objects.filter(id_heslo=subjectID)
            relatedObj = [Hesla.objects.get(id_heslo=related.pribuzny) for related in relatedID]
            relatedObj.sort(key=lambda subject: subject.heslo.lower())
            related = []
            if len(relatedObj) > 0:
                for obj in relatedObj:
                    related.append(u"<li itemid='%s' class='clickable'>%s</li>"%(obj.id_heslo, obj.heslo))
            else:
                related = none
            return conceptTable%(titleCS, acronym, titleEN, sysno, subjectID, "".join(nonprefCS), "".join(nonprefEN), "".join(related), broader, "".join(narrower))
            
        except Exception, e:
            return str(e)
    
def getWikipediaLink(request):
    """Check for wikipedia link"""
    subjectID = request.POST["subjectID"]
    try:
        link = Vazbywikipedia.objects.get(id_heslo=subjectID)
        return HttpResponse("True")
    except Exception, e:
        return HttpResponse(str(e))

def saveWikipediaLink(request):
    """Save wikipedia link"""
    subjectID = request.POST["subjectID"]
    try:
        heslo = Hesla.objects.get(id_heslo=subjectID)
        link = Vazbywikipedia(id_heslo=subjectID, heslo_wikipedia=heslo.heslo, uri_wikipedia="".join(["http://cs.wikipedia.org/wiki/", heslo.heslo]), typ_vazby="exactMatch")
        link.save()
        return HttpResponse("--- Wikipedia link saved ---")
    except Exception, e:
        return HttpResponse(str(e))

def update(request):
    """Update trigger"""
    handler.update()
    return render_to_response('update.html', {})