$(document).ready( function() {

    $('.vote-btn-question').click(function(){

        var id_qa = '#' + $(this).attr("id").substring(0, $(this).attr("id").length - 3);

        if ( $(this).hasClass("no-auth") ) {
           $(".alert").hide();
           $(this).parent().parent().prev().prev().show('medium');
           return;
        }

        if ( $(this).attr('data-author-id') == $('#user-id-field').html() ) {
           $(".alert").hide();
           $(this).parent().parent().prev().show('medium');
           return;
        }

        $.get('/vote/', {value: $(this).attr("value")}, function(data) {
            if (data != "None") {
                $(id_qa).html(data);
            }
        });
    });

    $('.by-date').click(function(){
        if ( $(this).hasClass("not-chosen") ) {
            $(this).addClass("chosen");
            $(this).removeClass("not-chosen");
            $('.by-trend').removeClass("chosen");
            $('.by-trend').addClass("not-chosen");
            $('#date-list').removeClass("hidden");
            $('#trend-list').addClass("hidden");
        }
    });


    $('.by-trend').click(function(){
        if ( $(this).hasClass("not-chosen") ) {
            $(this).addClass("chosen");
            $(this).removeClass("not-chosen");
            $('.by-date').removeClass("chosen");
            $('.by-date').addClass("not-chosen");
            $('#trend-list').removeClass("hidden");
            $('#date-list').addClass("hidden");
        }
    });

    $('.try-ask').click(function() {
        var num_of_tags = $('#id_tags').val().split(',').length;

        if (num_of_tags > 3) {
           $(".alert").hide();
           $('.alert-tags-errors').show('medium');
           return;
        };

        var len_of_text = $.trim($('#id_text').val()).length;

        if (len_of_text < 10) {
           $(".alert").hide();
           $('.alert-text-errors').show('medium');
           return;
        };

        $('.make-ask').click();
    });

    $('#id_title, #id_tags').keypress(function (e) {
        if (e.keyCode === 10 || e.keyCode === 13) {
            e.stopPropagation();
            e.preventDefault();

            var num_of_tags = $('#id_tags').val().split(',').length;
            if (num_of_tags > 3) {
                $(".alert").hide();
                $('.alert-tags-errors').show('medium');
                return;
            };

            var len_of_text = $.trim($('#id_text').val()).length;

            if (len_of_text < 10) {
               $(".alert").hide();
               $('.alert-text-errors').show('medium');
               return;
            };

            $('.make-ask').click();
        };
    });

    $('.try-answer').click(function() {

        var len_of_text = $.trim($('#id_text').val()).length;

        if (len_of_text < 10) {
           $(".alert").hide();
           $('.alert-text-errors').show('medium');
           return;
        };

        $('.make-answer').click();
    });


    $('.go-to-ask').click(function(e) {
        if ($( "#is-authenticated" ).html() != "True") {
            e.stopPropagation();
            e.preventDefault();
            $(".alert-ask-auth").hide();
            $('.alert-ask-auth').show('medium');
        }
    });

    $(function() {
        if ( $( "#date-list" ).length ) {
            $.get('/paginate_data/', {page: 1, data: 'd'}, function(data){
             $('#date-list').html(data);
            });
        };
     });

     $(function() {
        if ( $( "#trend-list" ).length ) {
            $.get('/paginate_data/', {page: 1, data: 't'}, function(data){
             $('#trend-list').html(data);
            });
        };
     });


     $(function() {
        if ( $( "#trending" ).length ) {
            $.get('/trending_data/', function(data){
             $('#trending').html(data);
            });
        };
     });

     $(function() {
        if ( $( "#search-render" ).length ) {
            $.get('/get_search/', { search: $( "#request-search-get" ).html() }, function(data){
             $("#search-render").html(data);
            });
        };
     });

    $(function() {
        if ( $( "#answers-for-question" ).length ) {
            $.get('/get_answers/', { question_id: $( "#question-id-div" ).html(),
                                    is_authenticated: $( "#is-authenticated" ).html()}, function(data){
             $("#answers-for-question").html(data);
            });

            setTimeout(function(){ $('#answer-form-id').removeClass('hidden');}, 200);
        };
     });


});
