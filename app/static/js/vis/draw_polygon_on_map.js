$(document).ready(function(){
  // TODO this part should be done byusing get request
  // get the color from get request from the server
  var inputJson;

  // set up the canvas size
  var cellWidth = 10;
  var cellHeight = 10;

  // canvas col and row num
  var dataX;
  var dataY;
  // original veg code
  var vegOrigin;
  // current veg code
  var vegCurrent;

  var canvasWidth;
  var canvasHeight;
  var canvasHandle;
  var canvas2DContext;

  // this is for define color for the cells
  var colorScale;

  // record the chosen area rec top left
  var firstPoint = {x:-1,y:-1};
  // record the chosen area rec bot right
  var secondPoint = {x:-1,y:-1};
  // record mouse click time
  var clickTime = 0;

  // this var record all the chosen HRU num
  var chosenHRU = [];
  // this struct array records chosen HRU and color
  // [{colorInfo:'#ffffff',HRUInfo:[1,2,3]},{...}]
  var chosenAreaInfo = [];

  // define google map with map
  var map;
  // this is for image overlay
  var imgOverlay;
  var imageBounds;
  // url for overlay image
  var imgURL;

  $.get('/api/base-veg-map', function(data){
    inputJson = data;

    // grab col and row num
    dataX = inputJson['projection_information']['ncol'];
    dataY = inputJson['projection_information']['nrow'];

    vegOrigin = obtainJsoninto1D(inputJson);

    // should not use var vegCurrent = vegOrigin
    // coz when we change vegCurrent and then vegOrigin will change too
    vegCurrent = vegOrigin.slice();

    canvasWidth = cellWidth*dataX;
    canvasHeight = cellHeight*dataY;
    // I am so confusing at this part...
    // If I change it into $('.mapCanvas').css('width',canvasWidth.toString()+'px');
    // then it only draw 30 boxes each line
    $('.mapCanvas').attr('width',canvasWidth.toString()+'px');
    $('.mapCanvas').attr('height',canvasHeight.toString()+'px');

    // place mapArray into canvas
    canvasHandle = document.getElementById("myCanvas");
    //var canvas2DContext = [];
    canvas2DContext = canvasHandle.getContext("2d");

    // this is for define color for the cells
    var scaleSize = Object.size(inputJson['vegetation_map']);
    colorScale = chroma.scale(['pink','black','blue','red','green']).colors(scaleSize);

    // add legend for the color panel
    for(var i=0; i<scaleSize; i++)
    {
      $("#colorLegendDiv").append("<p style='border-radius:25px;\
                                  padding:20px; \
                                  background:"+colorScale[i]+";'>\
                                  Legend for color "+i.toString()+"</p>");
    }

    // this part is used to push data into canvas
    // and paint color
    resetCanvas(vegOrigin);

    // overlay canvas on google map
    var latLonInformation = inputJson['projection_information'];
    // TODO map overlay works correctly
    overlayCanvasonGoogleMap(latLonInformation['xllcorner'],latLonInformation['xurcorner'],latLonInformation['yllcorner'],latLonInformation['yurcorner']);

    $("#myCanvas").click(function(evt){
      clickTime = clickTime + 1;
      var mousePos = getMousePos(canvasHandle, evt);
      changeCanvasCellColor(mousePos,"#FF00FF");
    });


    $("#resetCanvasButton").click(function(){
      resetCanvas(vegOrigin);
      vegCurrent = vegOrigin.slice();
      clickTime = 0;
      chosenHRU = [];
      chosenArea = [];

      updateMapOverlay();
    });

    $("#save-veg-update").click(function(){

      $.each(chosenAreaInfo, function(index1, value1) {
        //var tempColor = value1.colorNum;
        $.each(value1.chosenArea,function(index2,value2){

          vegCurrent[value2] = value1.colorNum;

        });
      });

      resetCanvas(vegCurrent);

      // update map overlay
      updateMapOverlay();
    });

    $("#submitChangetoServerButton").click(function(){
      // update json file based on the current HRU values
      updateJson();
      //var jsonStr = JSON.stringify(inputJson);
      $.ajax({
          type : "POST",
          url : "/api/base-veg-map",
          data: JSON.stringify(inputJson, null, '\t'),
          contentType: 'application/json;charset=UTF-8',
          success: function(result) {
              console.log(result);
          }
      });

    });

    // // users change color scale on the 2D map    
    // $("#colorConfirmButton").click(function(){
    //   // update color scale
    //   var startColor = $("#startColorID").val();
    //   var endColor = $("#endColorID").val();
    //   colorScale = chroma.scale([startColor,endColor]).colors(scaleSize);

    //   // add legend for the color panel
    //   for(var i=0; i<scaleSize; i++)
    //   {
    //     $("#colorPanel"+i.toString()).css("background-color:"+colorScale[i]);
    //   }


    //   resetCanvas(vegOrigin);

    //   updateMapOverlay();
    // });

    $("#removeOverlayButton").click(function(){
      removeOverlay();
    });

    $("#addOverlayButton").click(function(){
      addOverlay();
    });

    $("#changeOpacityButton").click(function(){
      changeOverlayOpacity();
    });

  });



  // this is used to find the length of an obj
  // this is from http://stackoverflow.com/questions/5223/length-of-a-javascript-object-that-is-associative-array
  Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
  };

  // this function is used to change json based on vegCurrent
  function updateJson()
  {
    var hruNum;
    var vegType;
    var objSize = Object.size(inputJson['vegetation_map']);
    // this for loop is for initialize the JSON HRU part
    for(var i=0; i<objSize; i++)
    {
      inputJson['vegetation_map'][i.toString()]['HRU_number'] = [];
    }

    // modify JSON HRU part
    for(var m=0 ; m<dataY ; m++)
      {
        for(var i=0 ; i<dataX ; i++)
        {
          hruNum = i + m*dataX;
          vegType = vegCurrent[hruNum];
          inputJson['vegetation_map'][vegType.toString()]['HRU_number'].push(hruNum);
        }
      }
  }


  // this function grab data json input and create a 1D array of hru values
  function obtainJsoninto1D(inputJson)
  {
    var outputArr = new Array(dataX*dataY);

    // for this case veg_code is the loop count (from 0), vegCode is str
    // therefore veg_code = i.toString()
    var tempSize;
    for(var i=0; i<Object.size(inputJson['vegetation_map']); i++)
    {
      tempSize = inputJson['vegetation_map'][i.toString()]['HRU_number'].length;
      for(var m=0; m<tempSize; m++ )
      {
        outputArr[inputJson['vegetation_map'][i.toString()]['HRU_number'][m]] = i;
      }
    }
    return outputArr;
  }

  // this is from http://www.html5canvastutorials.com/advanced/html5-canvas-mouse-coordinates/
  // get the mouse position, based on px
  function getMousePos(canvas, evt)
  {
    var rect = canvas.getBoundingClientRect();
    return {
      x: evt.clientX - rect.left,
      y: evt.clientY - rect.top
    };
  }

  // this function is used to refresh canvas with the original veg code
  function resetCanvas(colorMatrix)
  {
      for(var m=0 ; m<dataY ; m++)
      {
        for(var i=0 ; i<dataX ; i++)
        {
          canvas2DContext.fillStyle = colorScale[colorMatrix[i+dataX*m]];
          //                          start x,     y,            width,    height
          canvas2DContext.fillRect(cellWidth*i,cellHeight*m,cellWidth,cellHeight);
          // draw lines to separate cell
          canvas2DContext.rect(cellWidth*i,cellHeight*m,cellWidth,cellHeight);
        }
      }
      canvas2DContext.stroke();
  }

  // this function requires top left and bot right points for the chosen area
  function showChosenRecArea(input1,input2)
  {
    var p1 = {x:input1.x,y:input1.y};
    var p2 = {x:input2.x,y:input2.y};
    var temp;
    canvas2DContext.fillStyle = "#FFFF00";
    // not the same point
    if(p2.x!=p1.x&&p2.y!=p1.y)
    {
      if(p2.x < p1.x)
      {
        temp = p2.x;
        p2.x = p1.x;
        p1.x = temp;
      }
      if(p2.y < p1.y)
      {
        temp = p2.y;
        p2.y = p1.y;
        p1.y = temp;
      }
      // Here +1 coz need to count the bottom line too
      canvas2DContext.fillRect(p1.x*cellWidth, p1.y*cellHeight, cellWidth*(p2.x-p1.x+1), cellHeight*(p2.y-p1.y+1));
    }
    // two points in the same column
    else if(p2.x==p1.x&&p2.y!=p1.y)
    {
      if(p2.y < p1.y)
      {
        temp = p2.y;
        p2.y = p1.y;
        p1.y = temp;
      }
      // Here +1 coz need to count the bottom line too
      canvas2DContext.fillRect(p1.x*cellWidth, p1.y*cellHeight, cellWidth, cellHeight*(p2.y-p1.y+1));
    }
    // two points in the same row
    else if(p2.x!=p1.x&&p2.y==p1.y)
    {
      if(p2.x < p1.x)
      {
        temp = p2.x;
        p2.x = p1.x;
        p1.x = temp;
      }
      // Here +1 coz need to count the bottom line too
      canvas2DContext.fillRect(p1.x*cellWidth, p1.y*cellHeight, cellWidth*(p2.x-p1.x+1), cellHeight);
    }
    // push chosen HRU cell num
    recordChosenAreaInfo(p1,p2);

  }

  // this function is used to add the chosen cell number into chosenHRU
  // for this function p1.x and p1.y should be =< p2.x and p2.y
  // after this function chosenHRU may have some duplicated elements
  function recordChosenAreaInfo(p1,p2)
  {
    // get the current chosen color number
    var colorOptNum =
          parseInt($('input[name="vegcode-select"]:checked').val());

    for(var m=p1.y; m<=p2.y; m++)
    {
      for(var i=p1.x; i<=p2.x; i++)
      {
        chosenHRU.push(i+m*dataX);
      }
    }
    
    chosenAreaInfo.push({colorNum:colorOptNum,chosenArea:chosenHRU});
    chosenHRU=[];
  }

  function changeCanvasCellColor(mousePosition,color)
  {
    var startX = Math.floor(mousePosition.x/cellWidth);
    var startY = Math.floor(mousePosition.y/cellHeight);
    canvas2DContext.fillStyle = color;
    canvas2DContext.fillRect(startX*cellWidth, startY*cellHeight, cellWidth, cellHeight);

    if(clickTime == 1)
    {
      firstPoint.x = startX;
      firstPoint.y = startY;
    }
    else if(clickTime == 2)
    {
      secondPoint.x = startX;
      secondPoint.y = startY;

      showChosenRecArea(firstPoint,secondPoint);

    }
    else
    {
      firstPoint.x = secondPoint.x;
      firstPoint.y = secondPoint.y;

      secondPoint.x = startX;
      secondPoint.y = startY;

      showChosenRecArea(firstPoint,secondPoint);

    }
  }





});
