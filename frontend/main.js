// Add debug logging
console.log("Loading main.js");

$(document).ready(function () {
  // Log that the document is loaded
  console.log("Document ready, initializing UI");

  eel.init()();
  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

  // Hide the Oval section initially
  $("#Oval").hide();

  $("#MicBtn").click(function () {
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);

    eel.takeAllCommands()();
  });

  function doc_keyUp(e) {
    // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

    if (e.key === "j" && e.metaKey) {
      eel.play_assistant_sound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommands()();
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  function PlayAssistant(message) {
    if (message != "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      
      // Use the process_command function
      eel.process_command(message)().then(function(response) {
        // Don't automatically hide SiriWave - let the user go back manually
        console.log("Command processed:", response);
      }).catch(function(error) {
        console.error("Error processing command:", error);
      });
      
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  function ShowHideButton(message) {
    if (message.length == 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }
  // Expose the function to Python
  eel.expose(showMainInterface);
  function showMainInterface() {
      console.log("Showing main interface");
      
      // Hide all the authentication and loading elements
      $("#Loader").hide();
      $("#FaceAuth").hide();
      $("#FaceAuthSuccess").hide();
      $("#Start").hide();
      $("#HelloGreet").hide();
      
      // Show the main oval interface
      $("#Oval").show();
      console.log("Main interface displayed");
      
      // Trigger any initialization for the main interface
      setupMainInterface();
  }
  
  // Setup the main interface
  function setupMainInterface() {
      console.log("Setting up main interface");
      // Initialize any UI components
      
      // Focus the chat input
      $("#chatbox").focus();
  }

  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    console.log("Current chatbox input: ", message); // Log input value for debugging
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    key = e.which;
    if (key == 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });

  // Make sure other functions are properly defined
  eel.expose(hideLoader);
  function hideLoader() {
      console.log("Hiding loader");
      $("#Loader").hide();
  }
  
  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
      console.log("Hiding face auth");
      $("#FaceAuth").hide();
  }
  
  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
      console.log("Hiding face auth success");
      $("#FaceAuthSuccess").hide();
  }
  
  eel.expose(hideStart);
  function hideStart() {
      console.log("Hiding start");
      $("#Start").hide();
  }
  
  // Add event handler for back button
  $("#BackToHomeBtn").click(function() {
    console.log("Back button clicked");
    $("#SiriWave").attr("hidden", true);
    $("#Oval").attr("hidden", false);
    $("#chatbox").val("").focus();
  });

  // Call init function when page loads
  console.log("Calling init function");
  eel.init();
});
