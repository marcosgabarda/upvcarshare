import RRulesController from '../controllers/rrules';


const RRulesComponent = {
  controller: RRulesController,
  templateUrl: "/partials/journeys/rrules.html",
  bindings: {
    fieldName: '@',
    fieldId: '@',
    overrideDeparture: '<'
  }
};

export default RRulesComponent;
