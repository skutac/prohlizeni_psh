var currentSuggested = $('#suggestedSubjects li.hidden');
var screenheight = screen.height;

$(document).ready(function(){
    $('#scrollDiv, #scrollable').css('height', (screenheight-200));

    $('#concept_graph a').tagcloud({
      size: {start: 20, end: 50, unit: "pt"}, 
      color: {start: '#689AD3', end: '#071871'}
    });
    
    var subject = $("#heslo").text();
    var lang;
    if($("#czech").attr("class") == "active"){
      lang = "cs";
    }
    else{
      lang = "en";
    }

    $.ajax({
      url: 'get_library_records',
      type: 'GET',
      data: {subject:subject, lang:lang},
      success: function(records){
        $("#catalogue").append(records);
        $("#catalogue_records").hide();
        $("#catalogue_records").fadeIn();
      },
      
    });

      $("#search").delegate('#psh_suggest', 'keyup', function(event){
        var text_input = $(this).val();
        if(text_input.length > 1){
            var lang = $('#language').val();
            var keycode = (event.keyCode ? event.keyCode : event.which);

            if(keycode == '13'){
                var subject = $(this).val();
                $("#search_form").submit();
            }

            $.ajax({type : "GET",
                   url : "suggest",
                   datatype: "json",
                   success: function(subjects){
                          $("#psh_suggest").autocomplete({source: subjects});},
                   data : {'input': text_input, 'lang': lang}
            });
    }
    else{
        $("#suggestedSubjects").html("");
    }
    });

    // $('#english').click(function(){
    //     var lang = $('#language').val();

    //     if(lang == "cs"){
    //         $(this).css('opacity', '0.9');
    //         $('#search_language').text('angličitna');
    //         $('#language').val('en');
    //     }
    //     else{
    //         $(this).css('opacity', '0.2');
    //         $('#search_language').text('čeština');
    //         $('#language').val('cs');
    //     }
    // });
});

function getSuggestedSubject(subject){
    var lang = $('#english').attr('data-lang');
    $.ajax({type : "GET",
               url : "get_subject_id",
               success: function(subjectID){
                        if(subjectID == "None"){
                            $('#psh_suggest').val("");
                            $('ul.ui-autocomplete').hide();
                            getSearchResult(subject, english);
                        }
                        else{
                            var current = $('#' + subjectID);
                            getConcept(subjectID);
                            saveToCache(subject, subjectID);
                            unwrap(current);
                            highlight(current);
                            $('#psh_suggest').val("");
                        }
                       }, 
               data : {'input': subject, 'lang': lang}
    });
}

$('.ui-menu-item a').live('click', function(){
    var subject = $(this).text();
    getSuggestedSubject(subject);
});

function get_library_records_for_subject(){
    var subject = $("#heslo").text();
    $.ajax({
      url: '/get_library_records',
      type: 'GET',
      data: {subject: subject},
      success: function(records){
        $("#catalogue").append(records);
        $("#catalogue_records").hide();
        $("#catalogue_records").fadeIn();
      },
      
    });
    
}


// function getSearchResult(subject, english){
//     $.ajax({type : 'POST',
//               url : 'getSearchResult', 
//               success: function(subjects){
// //                        $('#concept').html(concept).hide();
//                           $('#concept').html(subjects);
// //                        $('#concept').fadeIn('slow');
//                        },
//               data : {substring : subject, english : english}
//       });
// }


// function checkWikipedia(subjectID){
//       var parent = $('#logoWikipedia').parent();
//       var subject = $('#' + subjectID).text();
//       var logoWikipedia = $('#logoWikipedia'); 
//       parent.removeAttr('href');
//       logoWikipedia.attr('class', 'inactive');
//       logoWikipedia.css('opacity', '0.3');
      
//       $.ajax({type: 'POST',
//               url: '/prohlizeni_psh/wikipedia',
//               data : {subjectID: subjectID},
//               success: function(msg){
// //                   console.log("---- Get wikipedia link:" + msg + " ----");
//                   if(msg == "True"){
//                     logoWikipedia.removeAttr('class');
//                     logoWikipedia.css('opacity', '1');
//                     parent.attr('href', 'http://cs.wikipedia.org/wiki/' + subject);
//                   }
//                   else{
//                     $.ajax({type : 'GET',
// 	                    dataType: 'jsonp',
//                             url : 'http://cs.wikipedia.org/w/api.php?action=opensearch&search=' + subject, 
//                             success: function(concept){
// 		              if(concept[1].length > 0){
// 		                  logoWikipedia.removeAttr('class');
// 		                  logoWikipedia.css('opacity', '1');
// 		                  parent.attr('href', 'http://cs.wikipedia.org/wiki/' + subject);
//                                   saveWikipediaLink(subjectID);
// 		              }
//                             },
//                             data : {}
//                     });
//                   }
//               }
//             });
// }

