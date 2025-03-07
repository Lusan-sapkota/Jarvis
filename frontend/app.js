// Consolidated JavaScript file

console.log("Loading app.js...");

$(document).ready(function() {
    console.log("Document ready - initializing UI functions");
    
    // Define UI functions for Eel to call
    window.showMainInterface = function() {
        console.log("showMainInterface called");
        
        // Hide all authentication screens
        $("#Loader").hide();
        $("#FaceAuth").hide();
        $("#FaceAuthSuccess").hide();
        $("#Start").hide();
        
        // Show main interface with animation
        $("#Oval").addClass("animate__animated animate__zoomIn");
        $("#Oval").show();
        $("#TextInput").show();
        
        console.log("Main interface should now be visible");
    };
    eel.expose(showMainInterface);
    
    // Define other UI functions
    window.hideLoader = function() {
        $("#Loader").hide();
    };
    eel.expose(hideLoader);
    
    window.hideFaceAuth = function() {
        $("#FaceAuth").hide();
    };
    eel.expose(hideFaceAuth);
    
    window.hideFaceAuthSuccess = function() {
        $("#FaceAuthSuccess").hide();
        // Show the greeting if it exists
        if($("#HelloGreet").length) {
            $("#HelloGreet").show();
        }
    };
    eel.expose(hideFaceAuthSuccess);
    
    window.hideStart = function() {
        $("#Start").hide();
    };
    eel.expose(hideStart);
    
    // Used for hotword activation visual feedback
    window.activateAssistant = function() {
        console.log("Assistant activated");
        $("#JarvisHood").addClass("active");
        setTimeout(function() {
            $("#JarvisHood").removeClass("active");
        }, 3000);
    };
    eel.expose(activateAssistant);
    
    // Handle button clicks
    $(document).on("click", "#MicBtn", function() {
        console.log("Mic button clicked - starting voice recognition");
        
        // Show visual feedback
        $("#Oval").addClass("active");
        $("#chatbox").val("Listening...");
        $("#chatbox").prop("disabled", true);
        
        // Call the listen_for_command function in Python
        eel.listen_for_command()(function(text) {
            console.log("Voice recognition result: " + text);
            
            // Remove the active class
            $("#Oval").removeClass("active");
            
            if (text) {
                // Show the recognized text briefly
                $("#chatbox").val(text);
                setTimeout(function() {
                    $("#chatbox").val("");
                }, 2000);
            } else {
                $("#chatbox").val("");
            }
            
            // Re-enable the input
            $("#chatbox").prop("disabled", false);
        });
    });
    
    $("#ChatBtn").click(function() {
        console.log("Chat button clicked - enabling text input");
        $("#chatbox").prop("disabled", false);
        $("#chatbox").val("");
        $("#chatbox").focus();
    });
    
    // Handle Enter key in chatbox
    $("#chatbox").keypress(function(e) {
        if(e.which === 13) { // Enter key
            const message = $(this).val().trim();
            if(message) {
                console.log("Sending message: " + message);
                eel.process_command(message);
                $(this).val("");
            }
            return false;
        }
    });
    
    // Initialize UI states
    $("#Oval").hide();
    $("#chatbox").prop("disabled", false);
    
    console.log("UI functions initialized");
});

// Function to show messages in UI
function displayMessage(text, isUser) {
    console.log((isUser ? "User" : "Assistant") + " message: " + text);
    // You could add a chat display area and show messages there
}