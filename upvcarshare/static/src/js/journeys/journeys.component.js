// Component for select origin and destination of a journey.
import {
  OriginDestinationSelectController,
  DatetimeController,
  DateController,
  TimeController,
  CalendarController,
  CircleMapController,
  RecurrenceCalendarController
} from './journeys.controller';


const OriginDestinationSelectComponent = {
  controller: OriginDestinationSelectController,
  templateUrl: "/partials/journeys/origin_destiny_select.html",
  bindings: {
    originField: '@',
    originFieldId: '@',
    destinyField: '@',
    destinyFieldId: '@'
  }
};


const DatetimeComponent = {
  controller: DatetimeController,
  templateUrl: "/partials/journeys/datetime.html",
  bindings: {
    value: '@',
    fieldName: '@',
    fieldId: '@',
    overrideValue: '<',
    onUpdate: '&',
    master: '='
  }
};


const DateComponent = {
  controller: DateController,
  templateUrl: "/partials/journeys/date.html",
  bindings: {
    value: '@',
    fieldName: '@',
    fieldId: '@',
  }
};


const TimeComponent = {
  controller: TimeController,
  templateUrl: "/partials/journeys/time.html",
  bindings: {
    value: '@',
    fieldName: '@',
    fieldId: '@',
  }
};


const CalendarComponent = {
  controller: CalendarController,
  templateUrl: "/partials/journeys/calendar.html",
  bindings: {
    userId: '@'
  }
};

const RecurrenceCalendarComponent = {
  controller: RecurrenceCalendarController,
  templateUrl: "/partials/journeys/recurrence_calendar.html",
  bindings: {
    journeyId: '@',
    onAddDay: '&',
    onDeleteDay: '&'
  }
};


const CircleMapComponent = {
  controller: CircleMapController,
  templateUrl: "/partials/journeys/circle_map.html",
  bindings: {
    radiusValue: '@',
    radiusField: '@',
    radiusFieldId: '@',
    positionValue: '@',
    positionField: '@',
    positionFieldId: '@',
    onUpdate: '&'
  }
};


export {OriginDestinationSelectComponent, DatetimeComponent, DateComponent, TimeComponent, CalendarComponent, CircleMapComponent, RecurrenceCalendarComponent};
