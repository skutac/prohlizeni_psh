var currentSuggested = $('#suggestedSubjects li.hidden');
var screenheight = screen.height;

$(document).ready(function(){
    $('#scrollDiv, #scrollable').css('height', (screenheight-200));
       
    var subject = $("#heslo").text();
    var lang;
    if($("#czech").attr("class") == "active"){
      lang = "cs";
    }
    else{
      lang = "en";
    }

    $.ajax({
      url: '/skos/get_library_records',
      type: 'GET',
      data: {subject:subject, lang:lang},
      success: function(records){
        $("#loading").fadeOut();
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
                   url : "/skos/suggest",
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

    $("#skos[rel]").overlay();
    $("#semantic_tag[rel]").overlay({left:"center", fixed:false});

    // $("#skos").click(function(){
    //   // $("#skos_format").dialog({modal:false, width: "auto", position: "center", resizable: false, show: "fade", stack: false});
    //   $("#skos_format").show();
    //   $("#skos_format").dialog({modal:false, width: "auto", position: "center", resizable: false, show: "fade", stack: false});
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