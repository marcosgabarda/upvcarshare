import {JoinAllOneController} from './journeys.controller';
import moment from 'moment';


const JourneyForm = () => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    scope.iAmDriver = "False";
    scope.newArrivalValue = null;

    scope.onUpdateDeparture = (value) => {
      // console.log("Updated departure: ", value);
      var newValue = moment(value).add(30, 'm');
      scope.newArrivalValue = newValue.toDate();
    };

  }
});

const JoinJourneyForm = ($uibModal) => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    // Initial value for join to value to one. It could be 'one' or 'all'
    scope.joinToValue = null;

    // Function to open modal
    function openModal() {
      var modalInstance = $uibModal.open({
        animation: true,
        templateUrl: 'join-all-one.html',
        controller: JoinAllOneController
      });
      modalInstance.result.then( (selectedOption) => {
        scope.joinToValue = selectedOption;
        var field = element.find("[name='join_to']");
        field.val(selectedOption);
        element.submit();
      });
    }

    // Link on submit form
    element.submit(() => {
      if (scope.joinToValue == null) {
        openModal();
        return false;
      }
      return true;
    });

  }
});
JoinJourneyForm.$inject = ["$uibModal"];

export {JourneyForm, JoinJourneyForm};
