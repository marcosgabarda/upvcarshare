import {JoinAllOneController, ConfirmRejectPassengerController} from './journeys.controller';
import moment from 'moment';


const SearchJourneyForm = () => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    if (attr.showTime !== undefined && attr.showTime !== null && attr.showTime !== "" && attr.showTime !== "None") {
      scope.showTime = attr.showTime;
    } else {
      scope.showTime = "False";
    }
    scope.toggleTime = () => {
      scope.showTime = scope.showTime == "False"? "True" : "False";
    };
  }
});

const JourneyForm = () => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    scope.iAmDriver = "False";
    scope.newArrivalValue = null;
    scope.newDepartureValue = null;

    scope.onUpdateDeparture = (value) => {
      scope.newDepartureValue = value;
      let newValue = moment(value).add(30, 'm');
      scope.newArrivalValue = newValue.toDate();
    };

  }
});

const ResidenceForm = () => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    scope.address = "";
    scope.onUpdateAddress = (value) => {
      scope.address = value;
    }
  }
});

const JoinJourneyForm = ($uibModal) => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    // Initial value for join to value to one. It could be 'one' or 'all'
    scope.joinToValue = null;
    scope.journeyId = attr.journeyId;

    // Function to open modal
    function openModal() {
      var modalInstance = $uibModal.open({
        animation: true,
        templateUrl: 'join-all-one.html',
        controller: JoinAllOneController,
        resolve: {
          journeyId: function () {
            return scope.journeyId;
          }
        }
      });
      modalInstance.result.then( (selectedOption) => {
        scope.joinToValue = selectedOption;
        if (typeof scope.joinToValue == "object"){
          scope.joinToValue = scope.joinToValue.join(",");
        }
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


const ConfirmPassengerForm = ($uibModal) => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    // Initial value for join to value to one. It could be 'one' or 'all'
    scope.confirmValue = null;

    // Function to open modal
    function openModal() {
      var modalInstance = $uibModal.open({
        animation: true,
        templateUrl: 'confirm-passenger.html',
        controller: ConfirmRejectPassengerController
      });
      modalInstance.result.then( (selectedOption) => {
        scope.confirmValue = selectedOption;
        element.submit();
      });
    }

    // Link on submit form
    element.submit(() => {
      if (scope.confirmValue == null) {
        openModal();
        return false;
      }
      return scope.confirmValue;
    });

  }
});
ConfirmPassengerForm.$inject = ["$uibModal"];


const RejectPassengerForm = ($uibModal) => ({
  restrict: 'A',
  link: (scope, element, attr) => {
    // Initial value for join to value to one. It could be 'one' or 'all'
    scope.rejectValue = null;

    // Function to open modal
    function openModal() {
      var modalInstance = $uibModal.open({
        animation: true,
        templateUrl: 'reject-passenger.html',
        controller: ConfirmRejectPassengerController
      });
      modalInstance.result.then( (selectedOption) => {
        scope.rejectValue = selectedOption;
        element.submit();
      });
    }

    // Link on submit form
    element.submit(() => {
      if (scope.rejectValue == null) {
        openModal();
        return false;
      }
      return scope.rejectValue;
    });

  }
});
RejectPassengerForm.$inject = ["$uibModal"];


export {JourneyForm, JoinJourneyForm, SearchJourneyForm, ConfirmPassengerForm,
  RejectPassengerForm, ResidenceForm};
