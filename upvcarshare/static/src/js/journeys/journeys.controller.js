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

  constructor() {
    this.picker = {
      date: new Date(),
      open: false,
      dateOptions: {
        startingDay: 1
      },
      timeOptions: {
        showMeridian: false
      }
    };
  }

  openCalendar($event) {
    this.picker.open = true;
  }

}

export {OriginDestinationSelectController, DatetimeController};
