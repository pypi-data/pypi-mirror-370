(function($) {
$.fn.m01GMapWidget = function (settings) {
    settings = $.extend({
        address: null,
        centerAfterInfoClose: true,
        iconAnchorXOffset: 0,
        iconAnchorYOffset: 0,
        iconHeight: null,
        iconShadowURL: null,
        iconURL: null,
        iconWidth: null,
        infoWindowAnchorXOffset: 0,
        infoWindowAnchorYOffset: 0,
        infoWindowContent: null,
        latitude: null,
        latitudeFallback: 10,
        latitudeExpression: null,
        longitude: null,
        longitudeFallback: 10,
        longitudeExpression: null,
        mapType: google.maps.MapTypeId.ROADMAP,
        mode: 'display',
        zoom: 11,
        zoomFallback: 4,
        useResizer: true,
        useResizerTrigger: true,
        responsive: true
    }, settings);

    // set initial vars
    var map = null;
    var marker = null;
    var infoWindow = null;
    var geocoder = null;
    var isInput = false;
    if (settings.mode == 'input') {
        isInput = true;
    }

    function setLatLong(latitude, longitude) {
        $(settings.latitudeExpression).val(latitude);
        $(settings.longitudeExpression).val(longitude);
    }

    function showInfo() {
        if (!infoWindow && settings.infoWindowContent) {
            infoWindow = new google.maps.InfoWindow({
                content: settings.infoWindowContent
                });
            infoWindow.open(map, marker);
        }
    }
    function closeInfo() {
        if (infoWindow) {
            infoWindow.close();
            infoWindow = null;
        }
    }

    function getGIcon() {
        var icon = null;
        if (settings.iconURL) {
            icon = new google.maps.MarkerImage(
                settings.iconURL,
                new google.maps.Size(settings.iconWidth, settings.iconHeight),
                new google.maps.Point(0,0),
                new google.maps.Point(settings.iconAnchorXOffset, settings.iconAnchorYOffset)
            );
            //if (settings.iconShadowURL) {
            //    icon.shadow = settings.iconShadowURL;
            //}
            //icon.infoWindowAnchor = new GPoint(
            //    settings.infoWindowAnchorXOffset,
            //    settings.infoWindowAnchorYOffset);
        }
        return icon;
    }

    function applyHandler() {
        google.maps.event.addListener(marker, "click", function() {
            showInfo();
        });
        if (settings.centerAfterInfoClose) {
            google.maps.event.addListener(marker, "infowindowclose", function() {
                var position = marker.getPosition();
                var lat = position.lat();
                var lng = position.lng();
                var point = new google.maps.LatLng(lat, lng);
                map.setCenter(point);
            });
        }
        if (isInput) {
            google.maps.event.addListener(marker, "dragstart", function() {
                closeInfo();
            });
            google.maps.event.addListener(marker, "dragend", function() {
                var position = marker.getPosition();
                var lat = position.lat();
                var lng = position.lng();
                setLatLong(lat, lng);
                point = new google.maps.LatLng(lat, lng);
                map.setCenter(point);
            });
        }
    }

    function setupMarkerPoint(point, zoom) {
        map.setZoom(zoom);
        icon = getGIcon();
        marker = new google.maps.Marker({
            position: point,
            map: map,
            icon: icon,
            draggable: isInput});

        applyHandler();
        setLatLong(point.lat(), point.lng());
        map.setCenter(point);
    }

    function setupMarkerPointCallback(results, status) {
        var point = null;
        var zoom = null;
        if (status == google.maps.GeocoderStatus.OK) {
            point = results[0].geometry.location
            zoom = map.getZoom();
        }else{
            point = new google.maps.LatLng(
                settings.latitudeFallback,
                settings.longitudeFallback);
            zoom = settings.zoomFallback;
        }
        setupMarkerPoint(point, zoom);
    }

    function setupMarker() {
        if (settings.latitude && settings.longitude) {
            var aPoint = new google.maps.LatLng(settings.latitude, settings.longitude);
            setupMarkerPoint(aPoint, settings.zoom);
        }else if (settings.address){
            geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': settings.address}, setupMarkerPointCallback);
        }else {
            alert("No initial address or latitude/longitude is given"); //p01.checker.silence
        }
    }

    function setupResizer() {
        google.maps.event.addDomListener(window, "resize", function() {
            var center = map.getCenter();
            google.maps.event.trigger(map, "resize");
            map.setCenter(center);
        });
    }

    // render the GMap
    function renderGMap(self) {
        if (settings.responsive) {
            $(self).width('100%');
        }
        var mapOptions = {
            mapTypeControl: true,
            zoomControl: true,
            mapTypeId: settings.mapType,
            zoom: settings.zoom
        }
        map = new google.maps.Map(self, mapOptions);
        setupMarker();
        if (settings.useResizer) {
            setupResizer();
        }
    }

    // render google maps
    return $(this).each(function(){
        var self = this;
        setTimeout(function() {
            // this timeout wrapper solves an issue with rendering the map
            // (the second time) in a dialog without page referesh
            renderGMap(self);
        }, 1);
        // prevent from memory leak
        $(window).on('beforeunload', function() {
            marker = null;
            infoWindow = null;
            map = null;
            geocoder = null;
        });
    });
};
})(jQuery);
