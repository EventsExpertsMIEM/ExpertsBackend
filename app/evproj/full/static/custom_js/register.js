$(function() {
    $("#f_register").submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: "/api/register_user",
            type: "POST",
            data: JSON.stringify({"mail": $(".register_user_mail").val(),
                                  "name": $(".register_user_name").val(),
                                  "surname": $(".register_user_surname").val(),
                                  "password": $(".register_user_password").val()
                                }),
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                $('#message').html(data["description"]);
                setTimeout(
                    function() {
                    window.location = '/login';
                    }, 2000
                )
            },
            error: function(data){
                $('#message').html(data.responseJSON['error']);
            }
        });
        $("#f_register").trigger('reset');
    });
});