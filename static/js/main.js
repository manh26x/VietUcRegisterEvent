(function ($) {

    "use strict";


    // Form
    var registerForm = function () {
        if ($('#registerForm').length > 0) {
            $("#registerForm").validate({
                rules: {
                    name: "required",
                    address: "required",
                    email: {
                        required: true,
                        email: true
                    },
                    num_attendees: {
                        required: true,
                        min: 1
                    }
                },
                messages: {
                    name: "Xin hãy nhập họ và tên",
                    address: "Xin hãy nhập địa chỉ",
                    email: "Xin hãy nhập email",
                    num_attendees: "Xin hãy nhập số người tham gia, tối thiểu 1"
                },
                /* submit via ajax */

                submitHandler: function (form) {
                    var $submit = $('.submitting'),
                        waitText = 'Xin đợi...';

                    $.ajax({
                        type: "POST",
                        url: "register",
                        data: $(form).serialize(),

                        beforeSend: function () {
                            $submit.css('display', 'block').text(waitText);
                        },
                        success: function (msg) {
                            debugger
                            $("#qr_img").attr('src', "data:image/png;base64," + msg.qr_code);
                            $('#down_img').attr('href', "data:image/png;base64," + msg.qr_code)
                            $('#myModal').modal('show');
                            $submit.css('display', 'none');
                        },
                        error: function () {
                            $('#form-message-warning').html("Something went wrong. Please try again.");
                            $('#form-message-warning').fadeIn();
                            $submit.css('display', 'none');
                        }
                    });
                } // end submitHandler

            });
        }
    };
    registerForm();


})(jQuery);

function clodeModal() {
    $('#myModal').modal('hide')
}

