
var Module;

if (typeof Module === 'undefined') Module = eval('(function() { try { return Module || {} } catch(e) { return {} } })()');

if (!Module.expectedDataFileDownloads) {
  Module.expectedDataFileDownloads = 0;
  Module.finishedDataFileDownloads = 0;
}
Module.expectedDataFileDownloads++;
(function() {
 var loadPackage = function(metadata) {

    var PACKAGE_PATH;
    if (typeof window === 'object') {
      PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
    } else if (typeof location !== 'undefined') {
      // worker
      PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
    } else {
      throw 'using preloaded data can only be done on a web page or in a web worker';
    }
    var PACKAGE_NAME = 'game.data';
    var REMOTE_PACKAGE_BASE = 'game.data';
    if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
      Module['locateFile'] = Module['locateFilePackage'];
      Module.printErr('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
    }
    var REMOTE_PACKAGE_NAME = typeof Module['locateFile'] === 'function' ?
                              Module['locateFile'](REMOTE_PACKAGE_BASE) :
                              ((Module['filePackagePrefixURL'] || '') + REMOTE_PACKAGE_BASE);
  
    var REMOTE_PACKAGE_SIZE = metadata.remote_package_size;
    var PACKAGE_UUID = metadata.package_uuid;
  
    function fetchRemotePackage(packageName, packageSize, callback, errback) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', packageName, true);
      xhr.responseType = 'arraybuffer';
      xhr.onprogress = function(event) {
        var url = packageName;
        var size = packageSize;
        if (event.total) size = event.total;
        if (event.loaded) {
          if (!xhr.addedTotal) {
            xhr.addedTotal = true;
            if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
            Module.dataFileDownloads[url] = {
              loaded: event.loaded,
              total: size
            };
          } else {
            Module.dataFileDownloads[url].loaded = event.loaded;
          }
          var total = 0;
          var loaded = 0;
          var num = 0;
          for (var download in Module.dataFileDownloads) {
          var data = Module.dataFileDownloads[download];
            total += data.total;
            loaded += data.loaded;
            num++;
          }
          total = Math.ceil(total * Module.expectedDataFileDownloads/num);
          if (Module['setStatus']) Module['setStatus']('Downloading data... (' + loaded + '/' + total + ')');
        } else if (!Module.dataFileDownloads) {
          if (Module['setStatus']) Module['setStatus']('Downloading data...');
        }
      };
      xhr.onload = function(event) {
        var packageData = xhr.response;
        callback(packageData);
      };
      xhr.send(null);
    };

    function handleError(error) {
      console.error('package error:', error);
    };
  
      var fetched = null, fetchedCallback = null;
      fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, function(data) {
        if (fetchedCallback) {
          fetchedCallback(data);
          fetchedCallback = null;
        } else {
          fetched = data;
        }
      }, handleError);
    
  function runWithFS() {

    function assert(check, msg) {
      if (!check) throw msg + new Error().stack;
    }
Module['FS_createPath']('/', 'img', true, true);

    function DataRequest(start, end, crunched, audio) {
      this.start = start;
      this.end = end;
      this.crunched = crunched;
      this.audio = audio;
    }
    DataRequest.prototype = {
      requests: {},
      open: function(mode, name) {
        this.name = name;
        this.requests[name] = this;
        Module['addRunDependency']('fp ' + this.name);
      },
      send: function() {},
      onload: function() {
        var byteArray = this.byteArray.subarray(this.start, this.end);

          this.finish(byteArray);

      },
      finish: function(byteArray) {
        var that = this;

        Module['FS_createDataFile'](this.name, null, byteArray, true, true, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change
        Module['removeRunDependency']('fp ' + that.name);

        this.requests[this.name] = null;
      },
    };

        var files = metadata.files;
        for (i = 0; i < files.length; ++i) {
          new DataRequest(files[i].start, files[i].end, files[i].crunched, files[i].audio).open('GET', files[i].filename);
        }

  
    function processPackageData(arrayBuffer) {
      Module.finishedDataFileDownloads++;
      assert(arrayBuffer, 'Loading data file failed.');
      assert(arrayBuffer instanceof ArrayBuffer, 'bad input to processPackageData');
      var byteArray = new Uint8Array(arrayBuffer);
      var curr;
      
        // copy the entire loaded file into a spot in the heap. Files will refer to slices in that. They cannot be freed though
        // (we may be allocating before malloc is ready, during startup).
        if (Module['SPLIT_MEMORY']) Module.printErr('warning: you should run the file packager with --no-heap-copy when SPLIT_MEMORY is used, otherwise copying into the heap may fail due to the splitting');
        var ptr = Module['getMemory'](byteArray.length);
        Module['HEAPU8'].set(byteArray, ptr);
        DataRequest.prototype.byteArray = Module['HEAPU8'].subarray(ptr, ptr+byteArray.length);
  
          var files = metadata.files;
          for (i = 0; i < files.length; ++i) {
            DataRequest.prototype.requests[files[i].filename].onload();
          }
              Module['removeRunDependency']('datafile_game.data');

    };
    Module['addRunDependency']('datafile_game.data');
  
    if (!Module.preloadResults) Module.preloadResults = {};
  
      Module.preloadResults[PACKAGE_NAME] = {fromCache: false};
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }
    
  }
  if (Module['calledRun']) {
    runWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
  }

 }
 loadPackage({"files": [{"audio": 0, "start": 0, "crunched": 0, "end": 1621036, "filename": "/background-monster.png"}, {"audio": 0, "start": 1621036, "crunched": 0, "end": 1843410, "filename": "/bush-normal.png"}, {"audio": 0, "start": 1843410, "crunched": 0, "end": 1845135, "filename": "/collidy.lua"}, {"audio": 0, "start": 1845135, "crunched": 0, "end": 2071330, "filename": "/game-over2.png"}, {"audio": 0, "start": 2071330, "crunched": 0, "end": 3801062, "filename": "/background-normal.png"}, {"audio": 0, "start": 3801062, "crunched": 0, "end": 3935375, "filename": "/splash1.png"}, {"audio": 0, "start": 3935375, "crunched": 0, "end": 4348883, "filename": "/bird-monster-attack.png"}, {"audio": 0, "start": 4348883, "crunched": 0, "end": 4469444, "filename": "/splash2.png"}, {"audio": 0, "start": 4469444, "crunched": 0, "end": 4894439, "filename": "/sky-normal.png"}, {"audio": 0, "start": 4894439, "crunched": 0, "end": 5074278, "filename": "/tree-monster.png"}, {"audio": 0, "start": 5074278, "crunched": 0, "end": 5258241, "filename": "/game-over1.png"}, {"audio": 0, "start": 5258241, "crunched": 0, "end": 5275847, "filename": "/bird-normal.png"}, {"audio": 0, "start": 5275847, "crunched": 0, "end": 5480256, "filename": "/lamp-monster.png"}, {"audio": 0, "start": 5480256, "crunched": 0, "end": 5633184, "filename": "/bush-monster.png"}, {"audio": 0, "start": 5633184, "crunched": 0, "end": 5902990, "filename": "/bird-monster.png"}, {"audio": 0, "start": 5902990, "crunched": 0, "end": 5909733, "filename": "/factory.lua"}, {"audio": 0, "start": 5909733, "crunched": 0, "end": 6138437, "filename": "/tree-normal.png"}, {"audio": 0, "start": 6138437, "crunched": 0, "end": 6559692, "filename": "/sky-monster.png"}, {"audio": 0, "start": 6559692, "crunched": 0, "end": 6565743, "filename": "/main.lua"}, {"audio": 0, "start": 6565743, "crunched": 0, "end": 6830150, "filename": "/rabbit-monster.png"}, {"audio": 0, "start": 6830150, "crunched": 0, "end": 8451186, "filename": "/img/background-monster.png"}, {"audio": 0, "start": 8451186, "crunched": 0, "end": 8673560, "filename": "/img/bush-normal.png"}, {"audio": 0, "start": 8673560, "crunched": 0, "end": 8899755, "filename": "/img/game-over2.png"}, {"audio": 0, "start": 8899755, "crunched": 0, "end": 10629487, "filename": "/img/background-normal.png"}, {"audio": 0, "start": 10629487, "crunched": 0, "end": 10763800, "filename": "/img/splash1.png"}, {"audio": 0, "start": 10763800, "crunched": 0, "end": 11177308, "filename": "/img/bird-monster-attack.png"}, {"audio": 0, "start": 11177308, "crunched": 0, "end": 11297869, "filename": "/img/splash2.png"}, {"audio": 0, "start": 11297869, "crunched": 0, "end": 11722864, "filename": "/img/sky-normal.png"}, {"audio": 0, "start": 11722864, "crunched": 0, "end": 11902703, "filename": "/img/tree-monster.png"}, {"audio": 0, "start": 11902703, "crunched": 0, "end": 12086666, "filename": "/img/game-over1.png"}, {"audio": 0, "start": 12086666, "crunched": 0, "end": 12104272, "filename": "/img/bird-normal.png"}, {"audio": 0, "start": 12104272, "crunched": 0, "end": 12308681, "filename": "/img/lamp-monster.png"}, {"audio": 0, "start": 12308681, "crunched": 0, "end": 12461609, "filename": "/img/bush-monster.png"}, {"audio": 0, "start": 12461609, "crunched": 0, "end": 12731415, "filename": "/img/bird-monster.png"}, {"audio": 0, "start": 12731415, "crunched": 0, "end": 12960119, "filename": "/img/tree-normal.png"}, {"audio": 0, "start": 12960119, "crunched": 0, "end": 13381374, "filename": "/img/sky-monster.png"}, {"audio": 0, "start": 13381374, "crunched": 0, "end": 13645781, "filename": "/img/rabbit-monster.png"}], "remote_package_size": 13645781, "package_uuid": "e46b2e2a-44c4-4e35-adac-da8c61d20f0d"});

})();
