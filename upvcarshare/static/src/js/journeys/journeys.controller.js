import moment from 'moment';


class OriginDestinationSelectController {

  constructor($scope, JourneyService) {
    this.$scope = $scope;
    this.journeyService = JourneyService;
  }

  $onInit() {
    this.residences = [];
    this.campus = [];

    this.originOptions = [];
    this.originSelected = null;
    this.originFieldValue = "";

    this.destinyOptions = [];
    this.destinySelected = null;
    this.destinyFieldValue = "";

    Promise.all(this.loadData()).then( () => {
      this.$scope.$apply( () => {
        this.buildOriginOptions();
      });
    });

  }

  // Load data
  loadData() {
    return [
      // Load residences
      this.journeyService.getResidences().then( response => {
        this.residences = response.results;
      }),
      // Load campus
      this.journeyService.getCampus().then( response => {
        this.campus = response.results;
      })
    ];
  }

  // Builds the list of available options for origin
  buildOriginOptions() {
    if (this.originSelected === null) {
      // If there is not origin, destination is disabled...
      this.originOptions = this.residences.concat(this.campus);
    }
  }

  changeOrigin() {
    if (this.campus.indexOf(this.originSelected) != -1) {
      this.originFieldValue = "campus:" + this.originSelected.id;
    } else if (this.residences.indexOf(this.originSelected) != -1) {
      this.originFieldValue = "residence:" + this.originSelected.id;
    }
    this.buildDestinyOptions();
  }

  changeDestiny() {
    if (this.campus.indexOf(this.destinySelected) != -1) {
      this.destinyFieldValue = "campus:" + this.destinySelected.id;
    } else if (this.residences.indexOf(this.destinySelected) != -1) {
      this.destinyFieldValue = "residence:" + this.destinySelected.id;
    }
  }

  // Builds the list of available options for destiny
  buildDestinyOptions() {
    if (this.campus.indexOf(this.originSelected) != -1) {
      // If there is selected a residence, only options for destiny are campus
      this.destinyOptions = this.residences;
    } else if (this.residences.indexOf(this.originSelected) != -1) {
      // If there is selected a residence, only options for destiny are residendes
      this.destinyOptions = this.campus;
    }
    if (this.destinyOptions.length > 0) {
      this.destinySelected = this.destinyOptions[0];
      this.changeDestiny();
    }
  }

}

OriginDestinationSelectController.$inject = ['$scope', 'JourneyService'];


class DatetimeController {

  constructor($scope) {
    this.scope = $scope;
  }

  $onInit() {
    const date = this.value !== undefined ? moment(this.value).toDate() : new Date();
    this.picker = {
      date: date,
      open: false,
      dateOptions: {
        startingDay: 1
      },
      timeOptions: {
        showMeridian: false
      },
      buttonBar: {
        show: true,
        now: {
          show: true,
          text: 'Ahora'
        },
        today: {
          show: true,
          text: 'Hoy'
        },
        clear: {
          show: true,
          text: 'Limpiar'
        },
        date: {
          show: true,
          text: 'Fecha'
        },
        time: {
          show: true,
          text: 'Hora'
        },
        close: {
          show: true,
          text: 'Cerrar'
        }
      }
    };
    // Call to onUpdate when $ctrl.picker.date changes.
    this.scope.$watch('$ctrl.picker.date', (previousValue, currentValue) => {
      // console.log("Watcher:", previousValue, currentValue)
      if (this.master) {
        if (currentValue !== undefined && previousValue !== currentValue) {
          this.onUpdate({"value": currentValue});
        }
        if (currentValue == undefined && previousValue !== undefined) {
          this.onUpdate({"value": previousValue});
        }
      }
    });
  }

  // Changes value of date when is set on parent
  $onChanges(changesObj) {
    if (changesObj.overrideValue.currentValue !== null && changesObj.overrideValue.currentValue !== undefined) {
      this.picker.date = changesObj.overrideValue.currentValue;
    }
  }

  openCalendar($event) {
    this.picker.open = true;
  }

}
DatetimeController.$inject = ['$scope'];


class DateController {

  constructor() {}

  $onInit() {
    var date = this.value !== undefined ? moment(this.value, "DD/MM/YYYY").toDate() : new Date();
    this.picker = {
      date: date,
      format: "dd/MM/yyyy",
      opened: false,
      dateOptions: {}
    };
  }

  openCalendar($event) {
    this.picker.opened = true;
  }

}


class TimeController {

  constructor() {}

  $onInit() {
    var date = this.value !== undefined ? moment(this.value, "HH:mm").toDate() : new Date();
    this.picker = {
      time: date,
      hStep: 1,
      mStep: 10,
      isMeridian: false
    };
  }

  changed($event) {}

  getTime () {
    return "" + moment(this.picker.time).format('H:mm');
  }

}


class CalendarController {

  constructor($scope, JourneyService, uiCalendarConfig) {
    this.journeyService = JourneyService;
    this.$scope = $scope;
    this.uiCalendarConfig = uiCalendarConfig;
  }

  processDataEvent(dataEvent) {
    var event = {
      "title": dataEvent.title,
      "start": moment(dataEvent.start).toDate(),
      "end": moment(dataEvent.end).toDate(),
      "url": `/journeys/${dataEvent.id}/`
    };
    if (dataEvent.user.id == parseInt(this.userId)) {
      if (dataEvent.disabled) {
        this.journeysCanceled.events.push(event);
      } else if (dataEvent.driver !== null) {
        this.journeysCreatedDriver.events.push(event);
      } else {
        this.journeysCreatedNoDriver.events.push(event);
      }
    } else {
      this.journeysJoined.events.push(event);
    }
  }

  // Load events
  loadEvents(url=null, mode=null) {
    this.loadingEvents = true;
    if (url === null) {
        this.journeyService.getJourneysJoined().then( (response) => {
        response.results.forEach((dataEvent) => {
          this.processDataEvent(dataEvent)
        });
        if (response.next !== null) {
          this.loadEvents(response.next, "joined");
        } else {
          this.loadingEvents = false;
          this.eventSources.push(this.journeysJoined);
        }
      });
      this.journeyService.getJourneysOwned().then( (response) => {
        response.results.forEach((dataEvent) => {
          this.processDataEvent(dataEvent)
        });
        if (response.next !== null) {
          this.loadEvents(response.next, "created");
        } else {
          this.loadingEvents = false;
          this.eventSources.push(this.journeysCreatedDriver);
          this.eventSources.push(this.journeysCreatedNoDriver);
          this.eventSources.push(this.journeysCanceled);
        }
      });
    } else {
      this.journeyService.getByUrl(url).then( (response) => {
        response.results.forEach((dataEvent) => {
          this.processDataEvent(dataEvent)
        });
        if (response.next !== null) {
          this.loadEvents(response.next, mode);
        } else {
          this.loadingEvents = false;
          if (mode == "created"){
            this.eventSources.push(this.journeysCreatedDriver);
            this.eventSources.push(this.journeysCreatedNoDriver);
            this.eventSources.push(this.journeysCanceled);
          }
          if (mode == "joined") this.eventSources.push(this.journeysJoined);
        }
      });
    }
  }

  // Change view
  changeView(view, calendar) {
    this.uiCalendarConfig.calendars[calendar].fullCalendar('changeView', view);
  }

  $onInit() {
    this.loadingEvents = false;
    this.eventSources = [];
    this.journeysCreatedDriver = {
      color: '#99c300',
      textColor: '#fff',
      events: []
    };
    this.journeysCreatedNoDriver = {
      color: '#ec6409',
      textColor: '#fff',
      events: []
    };
    this.journeysJoined = {
      color: '#01a5cb',
      textColor: '#fff',
      events: []
    };
    this.journeysCanceled = {
      color: '#818a91',
      textColor: '#fff',
      events: []
    };

    // Calendar config object
    this.uiConfig = {
      calendar: {
        editable: false,
        defaultView: "agendaWeek",
        locale: "es",
        header:{
          left: 'title',
          center: '',
          right: 'today prev,next'
        }
      }
    };
    this.loadEvents();
  }
}
CalendarController.$inject = ['$scope', 'JourneyService', 'uiCalendarConfig'];

/**
 * Controller for the map widget with a circle, to select the position and
 * distance, to make queries or update fields.
 */
class CircleMapController {

  constructor($scope, uiGmapGoogleMapApi) {
    this.scope = $scope;
    this.uiGmapGoogleMapApi = uiGmapGoogleMapApi;
  }

  changeCenter(latitude, longitude) {
    this.map.center = {
      latitude: latitude,
      longitude: longitude
    };
    this.circle.center = {
      latitude: latitude,
      longitude: longitude
    };
  }

  hasInitialCenter() {
    return !(this.positionValue == null || this.positionValue == undefined || this.positionValue == "None");
  }

  hasInitialRadius() {
    return this.radiusValue !== null && this.radiusValue !== undefined && this.radiusValue !== "None";
  }

  getInitialCenter() {
    const re = /POINT \(([0-9\-\.]+) ([0-9\-\.]+)\)/;
    const values = this.positionValue.match(re);
    if (values.length == 3) {
      return {
        latitude: parseFloat(values[2]),
        longitude: parseFloat(values[1])
      };
    }
    return null
  }

  getInitialRadius() {
    return parseFloat(this.radiusValue);
  }

  initializeMap() {
    if (!this.hasInitialCenter()) {
      // Initial position from geolocation
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition( (position) => {
          this.scope.$apply( () => {
            this.changeCenter(position.coords.latitude, position.coords.longitude);
          });
        });
      }
    }
  }

  positionObjectToGis(latitude, longitude) {
    return `POINT (${longitude} ${latitude})`;
  }

  $onInit() {
    // Map configuration
    this.map = {
      zoom: 16,
      center: {
          latitude: 39.4703669,
          longitude: -0.3749849,
      },
      options: {
        disableDefaultUI: false
      }
    };
    // Circle configuration
    this.circle = {
      center: {
          latitude: 39.4703669,
          longitude: -0.3749849,
      },
      radius: 200,
      stroke: {
        color: '#99c300',
        weight: 2,
        opacity: 1
      },
      fill: {
          color: '#99c300',
          opacity: 0.5
      },
      geodesic: true,
      draggable: true,
      clickable: true,
      editable: true,
      visible: true,
      control: {},
      events: {
        center_changed: () => {
          const value = this.circle.center;
          this.pointString = this.positionObjectToGis(value.latitude, value.longitude);
        }
      }
    };
    // Search box configuration
    this.searchbox = {
      template: 'searchbox.tpl.html',
      events: {
        places_changed: (searchBox) => {
          const places = searchBox.getPlaces();
          let place = {};
          if (places.length > 0) {
            place = places[0];
            this.changeCenter(
              place.geometry.location.lat(),
              place.geometry.location.lng()
            );
            if (this.onUpdate !== undefined) {
              this.onUpdate({value: place.formatted_address})
            }
          }
        }
      }
    };
    // Point string
    this.pointString = "";
    // Watch changes on circle center
    this.scope.$watch("$ctrl.circle.center", (value) => {
      if (value !== undefined) {
        this.pointString = this.positionObjectToGis(value.latitude, value.longitude);
      }
    });
    if (this.hasInitialCenter()) {
      this.map.center = this.getInitialCenter();
      this.circle.center = this.getInitialCenter();
    }
    if (this.hasInitialRadius()) {
      this.circle.radius = this.getInitialRadius();
    }
    // Load Google Maps
    this.uiGmapGoogleMapApi.then( (maps) => {
      this.maps = maps;
      this.initializeMap();
    });
  }
}
CircleMapController.$inject = ["$scope", "uiGmapGoogleMapApi"];


/**
 * Controller for the modal showed when a journey has repetitions.
 */
class JoinAllOneController {
  constructor($scope, $uibModalInstance, journeyId) {
    this.$scope = $scope;
    this.$uibModalInstance = $uibModalInstance;
    this.journeyId = journeyId;
  }

  $onInit() {
    this.$scope.selectedDates = [];
    this.$scope.one = ($event) => {
      this.$uibModalInstance.close("one");
    };
    this.$scope.all = ($event) => {
      this.$uibModalInstance.close("all");
    };
    this.$scope.some = ($event) => {
      if (this.$scope.selectedDates.length > 0 ) {
        this.$uibModalInstance.close(this.$scope.selectedDates);
      }
    };
    this.$scope.addedDay = (date) => {
      this.$scope.selectedDates.push(date.format("DD/MM/YYYY"));
    };
    this.$scope.removedDay = (date) => {
      this.$scope.selectedDates.splice(date.format("DD/MM/YYYY"), 1);
    };
  }
}
JoinAllOneController.$inject = ["$scope", "$uibModalInstance", 'JourneyService', 'uiCalendarConfig', 'journeyId'];


/**
 * Controller for the modal showed when a journey has repetitions.
 */
class LeaveAllOneController {
  constructor($scope, $uibModalInstance, journeyId) {
    this.$scope = $scope;
    this.$uibModalInstance = $uibModalInstance;
    this.journeyId = journeyId;
  }

  $onInit() {
    this.$scope.cancel = ($event) => {
      this.$uibModalInstance.dismiss(false);
    };
    this.$scope.one = ($event) => {
      this.$uibModalInstance.close("one");
    };
    this.$scope.all = ($event) => {
      this.$uibModalInstance.close("all");
    };
  }
}
LeaveAllOneController.$inject = ["$scope", "$uibModalInstance", 'journeyId'];


class RecurrenceCalendarController {

  constructor($scope, JourneyService, uiCalendarConfig) {
    this.$scope = $scope;
    this.journeyService = JourneyService;
    this.uiCalendarConfig = uiCalendarConfig;
  }

  processDataEvent(dataEvent) {
    var event = {
      "title": dataEvent.title,
      "start": moment(dataEvent.start).toDate(),
      "end": moment(dataEvent.end).toDate()
    };
    this.journeysDriver.events.push(event);
    this.eventDates.push(moment(dataEvent.start).format("DD/MM/YYYY"));
  }

  loadEvents(url=null,) {
    this.loadingEvents = true;
    if (url === null) {
      this.journeyService.getJourneyRecurrence(this.journeyId).then( (response) => {
        response.results.forEach((dataEvent) => {
          this.processDataEvent(dataEvent)
        });
        if (response.next !== null) {
          this.loadEvents(response.next);
        } else {
          this.loadingEvents = false;
          this.eventSources.push(this.journeysDriver);
        }
      });
    } else {
      this.journeyService.getByUrl(url).then( (response) => {
        response.results.forEach((dataEvent) => {
          this.processDataEvent(dataEvent)
        });
        if (response.next !== null) {
          this.loadEvents(response.next);
        } else {
          this.loadingEvents = false;
          this.eventSources.push(this.journeysDriver);
        }
      });
    }
  }

  $onInit() {
    // Selected events
    this.eventDates = [];
    this.selectedEvents = [];

    // Show calendar whith journey
    this.journeysDriver = {
      color: '#2980b9',
      textColor: '#fff',
      events: []
    };
    this.loadingEvents = false;
    this.eventSources = [];

    // Calendar config object
    this.uiConfig = {
      calendar: {
        editable: false,
        defaultView: "month",
        locale: "es",
        header:{
          left: 'title',
          center: '',
          right: 'today prev,next'
        },
        dayClick: (date, jsEvent, view) => {
          // If the date is valid
          var strDate = date.format("DD/MM/YYYY");
          if (this.eventDates.indexOf(strDate) !== -1) {
            if (this.selectedEvents.indexOf(strDate) !== -1) {
              $("td[data-date="+date.format('YYYY-MM-DD')+"]").removeClass("fc-state-highlight");
              this.selectedEvents.splice(this.selectedEvents.indexOf(strDate), 1);
              this.onDeleteDay({date: date});
            } else {
              $("td[data-date="+date.format('YYYY-MM-DD')+"]").addClass("fc-state-highlight");
              this.selectedEvents.push(strDate);
              this.onAddDay({date: date});
            }
          }
        }
      }
    };
    this.loadEvents();
  }
}
RecurrenceCalendarController.$inject = ["$scope", 'JourneyService', 'uiCalendarConfig'];


class ConfirmRejectPassengerController {
  constructor($scope, $uibModalInstance) {
    this.$scope = $scope;
    this.$uibModalInstance = $uibModalInstance;
  }

  $onInit() {
    this.$scope.selectedDates = [];
    this.$scope.continue = ($event) => {
      this.$uibModalInstance.close(true);
    };
    this.$scope.cancel = ($event) => {
      this.$uibModalInstance.dismiss(false);
    };
  }
}
ConfirmRejectPassengerController.$inject = ["$scope", "$uibModalInstance"];


class ConfirmThrowPassengerController {
  constructor($scope, $uibModalInstance) {
    this.$scope = $scope;
    this.$uibModalInstance = $uibModalInstance;
  }

  $onInit() {
    this.$scope.continue = ($event) => {
      this.$uibModalInstance.close(true);
    };
    this.$scope.cancel = ($event) => {
      this.$uibModalInstance.dismiss(false);
    };
  }
}
ConfirmThrowPassengerController.$inject = ["$scope", "$uibModalInstance"];


export {OriginDestinationSelectController, DatetimeController, TimeController,
  DateController, CalendarController, CircleMapController, JoinAllOneController,
  RecurrenceCalendarController, ConfirmRejectPassengerController,
  LeaveAllOneController, ConfirmThrowPassengerController};
