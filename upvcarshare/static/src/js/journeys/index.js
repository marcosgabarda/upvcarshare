import angular from 'angular';
import JourneyService from './journeys.service';
import {
  OriginDestinationSelectComponent,
  DatetimeComponent,
  DateComponent,
  TimeComponent,
  CalendarComponent,
  CircleMapComponent,
  RecurrenceCalendarComponent
} from './journeys.component';
import RRulesComponent from './components/rrules';
import {
  JourneyForm,
  JoinJourneyForm,
  SearchJourneyForm,
  ConfirmPassengerForm,
  RejectPassengerForm,
  ResidenceForm
} from './journey.directive';
import JoinAllOneController from './journeys.controller';

import 'lodash';
import 'angular-ui-bootstrap';
import 'bootstrap-ui-datetime-picker';
import 'angular-ui-calendar';
import 'angular-simple-logger';
import 'angular-google-maps';



const journeys = angular
  .module('journeys', [
    'ui.bootstrap',
    'ui.bootstrap.datetimepicker',
    'ui.calendar',
    'uiGmapgoogle-maps'
  ])

  .service('JourneyService', JourneyService)

  .controller('JoinAllOneController', JoinAllOneController)

  .component('originDestinationSelect', OriginDestinationSelectComponent)
  .component('journeyDatetime', DatetimeComponent)
  .component('journeyDate', DateComponent)
  .component('journeyTime', TimeComponent)
  .component('calendar', CalendarComponent)
  .component('circleMap', CircleMapComponent)
  .component('recurrenceCalendar', RecurrenceCalendarComponent)
  .component('rRules', RRulesComponent)

  .directive('journeyForm', JourneyForm)
  .directive('residenceForm', ResidenceForm)
  .directive('searchJourneyForm', SearchJourneyForm)
  .directive('joinJourneyForm', JoinJourneyForm)
  .directive('confirmPassengerForm', ConfirmPassengerForm)
  .directive('rejectPassengerForm', RejectPassengerForm)

  // Angular Google Maps
  .config(['uiGmapGoogleMapApiProvider', (uiGmapGoogleMapApiProvider) => {
    uiGmapGoogleMapApiProvider.configure({
      key: 'AIzaSyAUuXiJ-kthJMHdXerksxYbqIbrRFrVfG4',
      v: '3.24',
      libraries: 'geometry,visualization,places'
    });
  }]);


export default journeys;
