import React from "react";
import ReactDOM from "react-dom";
import AuthContainer from "../components/authentication-components";

export const AuthPage = () => {
  console.log(window.props);
  return (
    <React.StrictMode>
      <AuthContainer
        headline={window.props.headline}
        submitButtonLabel={window.props.submitButtonLabel}
        goToButtonLabel={window.props.goToButtonLabel}
        submitURL={window.props.submitURL}
        goToURL={window.props.goToURL}
        nextURL={window.props.nextURL}
        handleResponseHttpCodes={window.props.httpCodes}
        fieldNames={window.props.fieldNames}
        csrfToken={window.props.csrfToken}
      />
    </React.StrictMode>
  );
};

document.addEventListener("DOMContentLoaded", function () {
  ReactDOM.render(React.createElement(AuthPage), window.reactMount);
});
