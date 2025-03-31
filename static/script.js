$(document).ready(function() {
    function loadMessages() {
        $.getJSON("/get_messages", function(data) {
            $("#chatBox").empty();
            data.forEach(msg => {
                $("#chatBox").append(`<p><strong>${msg.username}:</strong> ${msg.message}</p>`);
            });
        });
    }

    $("#sendBtn").click(function() {
        const username = $("#username").val();
        const message = $("#message").val();
        if (!username || !message) return alert("Both fields required!");

        $.ajax({
            url: "/send",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ username, message }),
            success: function() {
                $("#message").val("");
                loadMessages();
            }
        });
    });

    setInterval(loadMessages, 2000);
});
