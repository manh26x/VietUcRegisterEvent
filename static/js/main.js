(function ($) {

    "use strict";

    // Form
    const registerForm = function () {
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
                            $("#qr_img").attr('src', "data:image/png;base64," + msg.qr_code);
                            $('#down_img').attr('href', "data:image/png;base64," + msg.qr_code);
                            localStorage.setItem('registered', 'true');
                            localStorage.setItem('qr_code', msg.qr_code);
                            localStorage.setItem('hashed_data', msg.hashed_data)
                            $('#myModal').modal('show');
                            $submit.css('display', 'none');

                        },
                        error: function () {
                            $('#form-message-warning').html("Something went wrong. Please try again.");
                            $('#form-message-warning').fadeIn();
                            $submit.css('display', 'none');
                            $(localStorage).set('registered', false);
                        }
                    });
                } // end submitHandler

            });
        }
    };
    registerForm();
$(document).ready(() => {
   if(localStorage.getItem('registered') === 'true') {
       $("#qr_img").attr('src', "data:image/png;base64," + localStorage.getItem('qr_code'));
    $('#down_img').attr('href', "data:image/png;base64," + localStorage.getItem('qr_code'));
           $('#myModal').modal('show');
   }
});





})(jQuery);

function clodeModal() {
    $('#myModal').modal('hide')
}

const cancelRegister = () => {
    const hashedStr = localStorage.getItem('hashed_data')
    if(confirm("Bạn có chắc muốn hủy đăng ký? ")) {
        $.ajax({
        type: 'DELETE',
        url: "/api/cancel/register/" + hashedStr,
        success: () => {
            localStorage.clear()
            alert('Hủy đăng ký thành công, bạn có thể đăng ký lại');
        },
        error: () => {
          alert('Có lỗi xảy ra khi hủy đăng ký!Xin hãy liên hệ với quản trị viên');
        }
    })
    } else {
    }
}
