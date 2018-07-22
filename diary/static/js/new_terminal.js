window.onkeyup = function(e) {
    var key = e.keyCode ? e.keyCode : e.which;

    if (key == 36) {
        window.location.replace("http://repreu17.pythonanywhere.com/home");
    };
}

term = new Terminal(
  {
    type: "POST",
    ps: '$',
    greeting: '%+rWith great power comes great responsibilty. %-r%n' +
              'Released under BSD License. %n(c) 2003-2013 termlib(http://www.masswerk.at/jsuix)%n' +
              '(c) 2014 Django Console - Anoop Thomas Mathew @atmb4u\n' +
              'Updated under GPL-3.0 License.%n' +
              '(c) 2018 Diary Console - Martin Stevko @MartinStevko',
    id: 1,
    termDiv: 'termDiv',
    crsrBlinkMode: true,
    handler: function () {
      this.newLine();
      var line = this.lineBuffer;
      var universe = this;

      $.ajax({
        url: 'console/post',
        type: "POST",
        data: {
          csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
          command: line
        },
        dataType: "json",
        complete: function (info) {
          universe.write(info.responseText);
          universe.prompt();
        }
      });
    }
  }
);
term.open();
