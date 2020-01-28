$(document).ready(function(){  
    $(document).on("click", ".b_action", function(){
        var page = $(this);
        var arr = page.attr('id').split(';');
        var str1 = $("#join_conf").text().replace().split("=");
        var str2 = $("#join_unconf").text().replace().split("=");
        $.ajax({
            url: "/api/guest_action",
            type: "POST",
            data: JSON.stringify({"user": arr[1],
                                  "event": arr[0],
                                  "action": arr[2]}),
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                if(data['status'] == 'ok') {
                    page.parents("tr").remove();
                    if (arr[2] == "confirmed") {
                        $("#join_conf").text(str1[0] + " = " + (Number(str1[1]) + 1).toString());
                    } else {
                        $("#join_unconf").text(str2[0] + " = " + (Number(str2[1]) + 1).toString());
                    }
                    
                }
            }
        });
    });
});