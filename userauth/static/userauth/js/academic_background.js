$(function () {
    var $academic_background = $('#id_academic_background');

    $academic_background.each(function() {
        if($(this).val() == 'other'){
            $('label[for=id_other], input#id_other').show();
        } else{
            $('label[for=id_other], input#id_other').hide();
        }
    });

    $academic_background.on('change', (function () {
       if($(this).val() == 'other'){
           $('label[for=id_other], input#id_other').show();
       } else {
           $('label[for=id_other], input#id_other').hide();
       }
    }));
});