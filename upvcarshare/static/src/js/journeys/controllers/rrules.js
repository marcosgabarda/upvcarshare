// Controlle for RRule component
import RRule from 'rrule';
import { SPANISH, gettext } from './rrules_i18n';


class RRulesController {

  constructor($scope) {
    this.$scope = $scope;
  }

  $onInit() {
    this.rrule = null;
    this.rruleString = null;
    this.rruleText = null;
    this.previousRRule = null;
    this.isActivated = false;
    this.dtstart = new Date();

    this.freqOptions = [
      {label: "Cada año", value: RRule.YEARLY},
      {label: "Cada mes", value: RRule.MONTHLY},
      {label: "Cada semana", value: RRule.WEEKLY},
      {label: "Cada día", value: RRule.DAILY}
    ]

    this.byweekdayOptions = [
      {label: "L", value: RRule.MO, model: false},
      {label: "M", value: RRule.TU, model: false},
      {label: "X", value: RRule.WE, model: false},
      {label: "J", value: RRule.TH, model: false},
      {label: "V", value: RRule.FR, model: false},
      {label: "S", value: RRule.SA, model: false},
      {label: "D", value: RRule.SU, model: false},
    ]

    this.wkstOptions = [
      {label: "L", value: RRule.MO, model: false},
      {label: "M", value: RRule.TU, model: false},
      {label: "X", value: RRule.WE, model: false},
      {label: "J", value: RRule.TH, model: false},
      {label: "V", value: RRule.FR, model: false},
      {label: "S", value: RRule.SA, model: false},
      {label: "D", value: RRule.SU, model: false},
    ]

    this.intervalOptions = [...Array(29).keys()].map(x => x + 1);
    this.intervalLabel = null;

    this.ends = "never";
  }

  $doCheck() {
    if (!this.isActivated) {
      this.previousRRule = this.rrule;
      this.rrule = null;
    } else if (this.rrule === null) {
      this.rrule = this.previousRRule !== null ? previousRRule : this.initialRRule();
    }
    if (this.rrule !== null) {
      this.updateIntervalLabel();
      this.updateByweekday();
      this.updateEnds();
      this.updateRRule();
    }
  }

  $onChanges(changesObj) {
    this.dtstart = this.overrideDeparture;
    if (this.rrule !== null && this.rrule !== undefined) {
      this.rrule.dtstart = this.overrideDeparture;
      this.updateRRule();
    }
  }

  updateEnds() {
    if (this.rrule !== null && this.rrule !== undefined) {
      if (this.ends ==  "never") {
        this.rrule.count = null;
        this.rrule.until = null;
      } else if (this.ends ==  "count") {
        this.rrule.until = null;
        if (this.rrule.count == null) this.rrule.count = 1;
      } else if (this.ends ==  "until") {
        this.rrule.count = null;
      }
    }
  }

  updateByweekday() {
    let byweekday = [];
    this.byweekdayOptions.map((option) => {
      if (option.model) {
        byweekday.push(option.value);
      }
    })
    this.rrule.byweekday = byweekday;
  }

  updateIntervalLabel() {
    if (this.rrule.freq == RRule.YEARLY) this.intervalLabel = "años";
    if (this.rrule.freq == RRule.MONTHLY) this.intervalLabel = "meses";
    if (this.rrule.freq == RRule.WEEKLY) this.intervalLabel = "semanas";
    if (this.rrule.freq == RRule.DAILY) this.intervalLabel = "días";
  }

  updateRRule() {
    if (this.rrule !== null) {
      const rrule = new RRule(this.rrule);
      this.rruleString = rrule.toString();
      this.rruleText = rrule.toText(gettext, SPANISH);
    }
  }

  initialRRule() {
    return {
      freq: this.freqOptions[2].value,
      byweekday: null,
      dtstart: this.dtstart,
      count: null,
      until: null
    }
  }
  hiddeByweekday() {
    if (this.rrule !== null) {
      return this.rrule.freq !== RRule.WEEKLY;
    }
    return false;
  }
}

RRulesController.$inject = ['$scope'];

export default RRulesController;
