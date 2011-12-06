var PSH = PSH || {};

PSH.Visualization = function (id_container, params) {
  // inicializace proměnných
  this.$container = $("#" + id_container);
  this.id_concept = params.id_concept || false;
  this.lang = params.lang || false; // "cs" nebo "en"
  this.canvas = false;
  this.canvaswidth = false; // cachování často užívaných DOM vlastností
  this.canvasheight = false;
  this.ctx = false;
  this.$textLayer = false;
  this.step = 0;
  this.side = -1; // "-1" vlevo, "1" vpravo

  if (!this.id_concept || !this.lang) {
    // Získání ID a jazyka z URL
    var url = document.location.href,
      re = new RegExp("(PSH|psh)[0-9]+"),
      match = re.exec(url);
    this.id_concept = match ? match[0] : false;
    this.lang = url.match("en") ? "en" : "cs";
  }

  // vytvoření textové vrstvy
  this.$textLayer = $("<ul></ul>");
  this.$textLayer.attr("id", "textLayer");
  this.$container.append(this.$textLayer);

  // vytvoření elementu <canvas>
  this.canvas = document.createElement("canvas");
  this.canvas.width = this.$container.width();
  this.canvaswidth = this.canvas.width;
  this.canvasheight = this.canvas.height;

  var fallbackContent = document.createTextNode("Váš prohlížeč nepodporuje vykreslování grafiky pomocí JavaScriptu. Zvažte prosím povýšení na modernější prohlížeč.");
  this.canvas.appendChild(fallbackContent);

  this.$container.append(this.canvas);

  // navázání metody getContext na canvas v IE
  if (typeof G_vmlCanvasManager !== "undefined") {
    G_vmlCanvasManager.initElement(this.canvas);
  }
  
  if (this.canvas.getContext) {
    this.ctx = this.canvas.getContext("2d");
  }
};

PSH.Visualization.prototype = {
  drawBezierPath : function (startX, startY, endX, endY, side, orientation) {
    var cp1x = startX,
      cp1y = endY + orientation * 50,
      cp2x = startX + (side * 50),
      cp2y = endY;
    this.ctx.beginPath();
    this.ctx.moveTo(startX, startY);
    this.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, endX, endY);
    this.ctx.stroke();
  },
  drawCircle : function (conceptWidth, x0, y0) {
    // Vykreslení kruhu pod hlavním heslem
    var that = this;
    var arc = function() {
      that.ctx.arc(
        x0 + 1,
        y0 + 3,
        (conceptWidth / 3) * 2,
        0,
        2 * Math.PI,
        0
      );
    };
    this.ctx.beginPath();
    this.ctx.fillStyle = "rgba(255, 255, 255, 1)";
    arc();
    this.ctx.fill();
    this.ctx.beginPath();
    arc();
    this.ctx.stroke();
  },
  drawLine : function (startX, startY, endX, endY) {
    this.ctx.beginPath();
    this.ctx.moveTo(startX, startY);
    this.ctx.lineTo(endX, endY);
    this.ctx.stroke();
  },
  display : function (data) {
    var id = data.id_heslo,
      concept = data.heslo,
      related = data.pribuzny,
      broader = data.nadrazeny,
      narrower = data.podrazeny;

    // Vytvoření DOMu
    var $concept = $("<li>" + concept + "</li>");
    $concept.attr("id", "heslo");

    this.$textLayer.append($concept);

    // Rozměry a pozice hesla
    var conceptHeight = $concept.height(),
      conceptWidth = $concept.width(),
      conceptLeftOffset = (this.canvaswidth - conceptWidth) / 2,
      conceptTopOffset = related ? (((related.length + (related.length % 2)) / 2 * conceptHeight) + conceptWidth) : conceptWidth,
      x0 = conceptLeftOffset + conceptWidth / 2,
      y0 = conceptTopOffset + conceptHeight / 2;

    // Odsazení hesla
    $concept.css({
      "left" : conceptLeftOffset,
      "top" : conceptTopOffset
    });

    // Nastavení výšky canvasu
    $(this.canvas).attr(
      "height",
      (15 + narrower.length) * conceptHeight
    );

    // Nadřazené heslo
    if (broader) {
      broader = broader[0];
      var $broader = $("<li></li>"),
        $broaderLink = $("<a>" + broader.heslo + "</a>");
      $broaderLink.attr({
        "class" : "nadrazeny",
        "href" : "/skos/" + broader.id_heslo + "/html/" + this.lang
      });
      $broader.append($broaderLink);
      this.$textLayer.append($broader);

      // Rozměry a pozice
      var broaderWidth = $broaderLink.width(),
        broaderHeight = $broaderLink.height(),
        broaderX = this.canvaswidth / 2,
        broaderY = broaderHeight,
        broaderLeftOffset = broaderX - (broaderWidth / 2);
      $broaderLink.css({
        "top" : "0px",
        "left" : broaderLeftOffset
      });
      this.drawLine(x0, y0, broaderX, broaderY);
    }

    // Reference na objekt pro odkazování z vnitřku funkcí
    var that = this;
    
    // Příbuzná hesla
    $.each(related, function (key, value) {
      var $related = $("<li></li>"),
        $relatedLink = $("<a>" + value.heslo + "</a>");
      $relatedLink.attr({
        "class" : "pribuzny",
        "href" : "/skos/" + value.id_heslo + "/html/" + that.lang
      });
      $related.append($relatedLink);
      that.$textLayer.append($related);
      
      var relatedWidth = $relatedLink.width() + 20,
        relatedHeight = $relatedLink.height(),
        relatedX = that.canvaswidth / 2 * (that.side + 1) - that.side * relatedWidth,
        relatedY = that.step + 3 * relatedHeight / 2,
        relatedLeftOffset = (that.side + 1) / 2 * (that.canvaswidth - relatedWidth),
        relatedTopOffset = that.step + relatedHeight;
      $relatedLink.css({
        "left" : relatedLeftOffset,
        "top" : relatedTopOffset
      });
      that.drawBezierPath(x0, y0, relatedX, relatedY, that.side, 1);

      if (that.side === 1) {
        that.step += 1.5 * relatedHeight;
      }
      // Přehození stran
      that.side *= -1;
    });

    // Podřazená hesla
    that.side = -1;
    that.step = y0 + 2 * conceptHeight;
    $.each(narrower, function (key, value) {
      var $narrower = $("<li></li>"),
        $narrowerLink = $("<a>" + value.heslo + "</a>");
      $narrowerLink.attr({
        "class" : "podrazeny",
        "href" : "/skos/" + value.id_heslo + "/html/" + that.lang
      });
      $narrower.append($narrowerLink);
      that.$textLayer.append($narrower);

      // Rozměry a pozice
      var narrowerWidth = $narrowerLink.width() + 20,
        narrowerHeight = $narrowerLink.height(),
        narrowerX = that.canvaswidth / 2 * (that.side + 1) - that.side * narrowerWidth,
        narrowerY = that.step + narrowerHeight / 2,
        narrowerLeftOffset = (that.side + 1) / 2 * (that.canvaswidth - narrowerWidth),
        narrowerTopOffset = that.step;
      $narrowerLink.css({
        "left" : narrowerLeftOffset,
        "top" : narrowerTopOffset
      });
      that.drawBezierPath(x0, y0, narrowerX, narrowerY, that.side, -1);
      if (that.side === 1) {
        that.step += 1.5 * narrowerHeight;
      }
      // Přehození stran
      that.side *= -1;
    });

    // Kruh okolo hesla
    this.drawCircle(conceptWidth, x0, y0);
  },
  load : function (callback, params) {
    $.ajax({
      data : (params && params.data) ? params.data : {
        "lang" : this.lang,
        "subject_id" : this.id_concept
      },
      dataType : "jsonp",
      jsonpCallback : callback,
      url : (params && params.url) ? params.url : "http://data.ntkcz.cz/prohlizeni_psh/getjson"
    });
  }
};
