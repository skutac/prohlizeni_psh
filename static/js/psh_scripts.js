var currentSuggested = $('#suggestedSubjects li.hidden');
var screenheight = screen.height;
$(document).ready(function(){
    $('#scrollDiv, #scrollable').css('height', (screenheight-200));
//     $('#mainTree').load('/prohlizeni_psh/static/html/tree.html', function(){
//         var test = $('#pshID').text();
//         if(test.length == 0){
//             getConcept("PSH1");
// 	   checkWikipedia('PSH1');
//         }
//         else{
//             var subjectID = test;
//             var subject = $("#titleCS").text();
//             var current = $('#' + subjectID);
//             unwrap(current);
//             highlight(current);
//         }
//     });
/*

    $('#mainTree').delegate('.heslo', 'click', function() {
      var subjectID = $(this).attr('id');
      var current = $(this);
      var subject = current.text();
      getConcept(subjectID);
      saveToCache(subject, subjectID);
      var test = $(current).next();
      if(test.get(0) != undefined){ 
        if(test.get(0).nodeName == 'UL'){
        if(test.is(":visible")){
            test.slideUp('slow');
            $(this).css('background-image', 'url(/prohlizeni_psh/static/img/1.png)');
        }
        else{
            test.slideDown('slow');
            $(this).css('background-image', 'url(/prohlizeni_psh/static/img/1_down.png)');
        }
      }}
      highlight(current);*/
      $("#search").delegate('#pshSuggest', 'keyup', function(event){
        var textInput = $(this).val();
        if(textInput.length > 1){
        var lang = $('#english').attr('data-lang');
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            var subject = $(this).val();
            getSuggestedSubject(subject);
        }
        $.ajax({type : "GET",
               url : "/prohlizeni_psh/suggest",
               datatype: "json",
               success: function(subjects){
                      $("#pshSuggest").autocomplete({source: subjects});},
               data : {'input': textInput, 'lang': lang}
        });
    }
    else{
        $("#suggestedSubjects").html("");
    }
    });
});

function getSuggestedSubject(subject){
    var lang = $('#english').attr('data-lang');
    $.ajax({type : "GET",
               url : "/prohlizeni_psh/get_subject_id",
               success: function(subjectID){
                        if(subjectID == "None"){
                            $('#pshSuggest').val("");
                            $('ul.ui-autocomplete').hide();
                            getSearchResult(subject, english);
                        }
                        else{
                            var current = $('#' + subjectID);
                            getConcept(subjectID);
                            saveToCache(subject, subjectID);
                            unwrap(current);
                            highlight(current);
                            $('#pshSuggest').val("");
                        }
                       }, 
               data : {'input': subject, 'lang': lang}
    });
}

function getSearchResult(subject, english){
    $.ajax({type : 'POST',
              url : '/prohlizeni_psh/getSearchResult', 
              success: function(subjects){
//                        $('#concept').html(concept).hide();
                          $('#concept').html(subjects);
//                        $('#concept').fadeIn('slow');
                       },
              data : {substring : subject, english : english}
      });
}

$('.ui-menu-item a').live('click', function(){
    var subject = $(this).text();
    getSuggestedSubject(subject);
});

$('#english').live('click', function(){
    var lang = $(this).attr('data-lang');
    if(lang == "cs"){
        $(this).css('opacity', '0.9');
        $(this).attr('data-lang', 'en');
        $('#searchLanguage').text('angličitna');
    }
    else{
        $(this).css('opacity', '0.2');
        $(this).attr('data-lang', 'cs');
        $('#searchLanguage').text('čeština');
    }
});

// $('.clickable').live('click', function() {
//       var subjectID = $(this).attr('itemid');
//       var subject = $(this).text();
//       var current = $('#' + subjectID);
//       getConcept(subjectID);
//       saveToCache(subject, subjectID);
//       unwrap(current);
//       highlight(current);
// });

// $('#cacheList li').live('click', function() {
//     var subjectID = $(this).attr('itemid');
//     var current = $('#' + subjectID);
//     getConcept(subjectID);
//     unwrap(current);
//     highlight(current);
// });

function setMARCLink(){
    var sysno = $("#pshID").attr("data-sysno");
    $("#marc_link").attr("href", "http://aleph.techlib.cz/F?func=direct&local_base=STK10&doc_number=" + sysno + "&format=001");
    return
}

function saveToCache(subject, subjectID){
    var test = $('.cache').filter(function() {
        return $(this).attr('itemid') == subjectID;
    });
    if(test.text() == ""){
        var cache = $('#cacheList li.active');
        cache.text(subject);
        cache.attr('itemid', subjectID);
        cache.attr('class', 'inactive cache');
        var nextCache = $(cache).next();
        if(nextCache.get(0) != undefined){
            nextCache.attr('class', 'active cache');
        }
        else{
            $('#cacheList li:first').attr('class', 'active cache');
        }
    }
}

function highlight(li){
    $('li').css('color', 'black');
    li.css('color', 'red');
    var subject = li.text();
    var subjectID = li.attr('id');
//     alert(li.offset().top);
//     alert($('#scrollable').scrollTop());
    $('#katalog').parent().attr('href','http://aleph.techlib.cz/F/?func=find-b&request=' + encodeURIComponent(subject) + '&find_code=PSH&adjacent=N&local_base=STK&x=26&y=5&filter_code_1=WLN&filter_request_1=&filter_code_2=WYR&filter_request_2=&filter_code_3=WYR&filter_request_3=&filter_code_4=WFM&filter_request_4=&filter_code_5=WSL&filter_request_5=&pds_handle=GUEST');
    $('#scrollable').animate({scrollTop:($('#scrollable').scrollTop() + li.offset().top - screenheight/2)}, 1000);
}

// function getConcept(subjectID){
//     $.ajax({type : 'POST',
//               url : '/prohlizeni_psh/getConcept', 
//               success: function(concept){
//                        $('#concept').html(concept).hide();
//                        checkWikipedia(subjectID);
//                        setMARCLink();
//                        $('#concept').fadeIn('slow');
//                        },
//               data : {subjectID : subjectID}
//       });
// }

function unwrap(current){
      var test = $(current).next();
      $(current).parents().show('slow');
      $(current).parents('ul').each(function(){
//       $(this).show('slow');
      $(this).prev('li').css('background-image', 'url(/prohlizeni_psh/static/img/1_down.png)');
      });
      if(test.get(0) != undefined){ 
        if(test.get(0).nodeName == 'UL'){
        if(test.is(":hidden")){
            test.slideDown('slow');
            $(current).css('background-image', 'url(/prohlizeni_psh/static/img/1_down.png)');
        }
      }}
     return false; 
}

function checkWikipedia(subjectID){
      var parent = $('#logoWikipedia').parent();
      var subject = $('#' + subjectID).text();
      var logoWikipedia = $('#logoWikipedia'); 
      parent.removeAttr('href');
      logoWikipedia.attr('class', 'inactive');
      logoWikipedia.css('opacity', '0.3');
      
      $.ajax({type: 'POST',
              url: '/prohlizeni_psh/wikipedia',
              data : {subjectID: subjectID},
              success: function(msg){
//                   console.log("---- Get wikipedia link:" + msg + " ----");
                  if(msg == "True"){
                    logoWikipedia.removeAttr('class');
                    logoWikipedia.css('opacity', '1');
                    parent.attr('href', 'http://cs.wikipedia.org/wiki/' + subject);
                  }
                  else{
                    $.ajax({type : 'GET',
	                    dataType: 'jsonp',
                            url : 'http://cs.wikipedia.org/w/api.php?action=opensearch&search=' + subject, 
                            success: function(concept){
		              if(concept[1].length > 0){
		                  logoWikipedia.removeAttr('class');
		                  logoWikipedia.css('opacity', '1');
		                  parent.attr('href', 'http://cs.wikipedia.org/wiki/' + subject);
                                  saveWikipediaLink(subjectID);
		              }
                            },
                            data : {}
                    });
                  }
              }
            });
}

function saveWikipediaLink(subjectID){
//     console.log("---- Saving wikipedia link: " + subjectID + " ----");
    $.ajax({type: 'POST',
            url: '/prohlizeni_psh/saveWikipediaLink',
            success: function(msg){
//                 console.log(msg);
            },
            data: {subjectID:subjectID},
    });
}

