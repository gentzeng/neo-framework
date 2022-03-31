import React, { useState } from "react";
import PropTypes from "prop-types";
import capitalizeFirstLetter from "../utils/string-utils";
export { AuthContainer as default };
import { restCreate } from "../api/rest-api-consumation";

const divClass = "m-auto col-xl-6 col-lg-6 col-md-8 col-sm-10 col-12";
const errorDivClass = "d-block py-1 mb-2 alert alert-danger";

export const AuthContainer = ({
  headline,
  submitButtonLabel,
  goToButtonLabel,
  submitURL,
  goToURL,
  nextURL,
  handleResponseHttpCodes,
  fieldNames,
  csrfToken,
}) => {
  const [errors, setErrors] = useState({});
  const onSubmit = async (event) => {
    event.preventDefault(); // prevent default behavior of form submit
    const form = event.target;
    const data = new FormData(form);

    const response = await restCreate({
      url: submitURL,
      data: data,
      authorize: false,
    });
    handleResponse(response, handleResponseHttpCodes);
  };

  const handleResponse = (response, httpCodes) => {
    const [status, json] = response;
    if (httpCodes.successGoToNext.includes(status)) {
      window.location.href = nextURL;
    } else if (httpCodes.clientErrors.includes(status)) {
      setErrors(json);
    } else if (status === 500) {
      setErrors({
        non_field_errors: "There was a server error. Please try again!",
      });
    }
  };

  return (
    <React.StrictMode>
      <div className="container" id="content-container">
        <div className="row d-flex justity-content-center mb-4">
          <h2 className="text-center text-white">{headline}</h2>
          <ErrorWindow errors={errors} />
          <div className={divClass}>
            <form onSubmit={onSubmit}>
              <CsrfTokenInput csrfToken={csrfToken} />
              <AuthFields fieldNames={fieldNames} errors={errors} />
              <ButtonArea>
                <SubmitButton label={submitButtonLabel} />
                <GoToButton label={goToButtonLabel} url={goToURL} />
              </ButtonArea>
            </form>
          </div>
        </div>
      </div>
    </React.StrictMode>
  );
};
AuthContainer.propTypes = {
  headline: PropTypes.string,
  submitButtonLabel: PropTypes.string,
  goToButtonLabel: PropTypes.string,
  submitURL: PropTypes.string,
  goToURL: PropTypes.string,
  nextURL: PropTypes.string,
  handleResponseHttpCodes: PropTypes.object,
  fieldNames: PropTypes.array,
  csrfToken: PropTypes.string,
};

export const AuthFields = ({ fieldNames, errors }) => {
  return (
    <React.StrictMode>
      {fieldNames.map((fieldName) => {
        return (
          <AuthField
            key={fieldName}
            fieldName={fieldName}
            errorMsg={errors[fieldName]}
          />
        );
      })}
    </React.StrictMode>
  );
};
AuthFields.propTypes = {
  fieldNames: PropTypes.array,
  errors: PropTypes.object,
};

const AuthField = ({ fieldName, errorMsg }) => {
  const id = `id${fieldName}`;
  const label = capitalizeFirstLetter(fieldName.replace(/_/g, " "));
  const getType = (fieldName) => {
    if (["password", "confirm_password"].includes(fieldName)) {
      return "password";
    } else if (fieldName === "email") {
      return "email";
    }
    return "text";
  };
  return (
    <React.StrictMode>
      <div className="row justify-content-end mb-1">
        <label className="col-sm-4 col-form-label text-white" htmlFor={id}>
          {label}
        </label>
        <div className="col-sm-8">
          <input
            id={id}
            name={fieldName}
            type={getType(fieldName)}
            className="form-control"
            autoComplete="on"
          />
        </div>
        <div className="col-sm-8" id={`${id}ErrorField`}>
          {typeof errorMsg == "undefined" ? null : (
            <div className="d-block py-1 mb-2 text-danger">{errorMsg}</div>
          )}
        </div>
      </div>
    </React.StrictMode>
  );
};
AuthField.propTypes = {
  fieldName: PropTypes.string,
  errorMsg: PropTypes.string,
};

const ButtonArea = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="d-grip gap-2 d-flex justify-content-between">
        {children}
      </div>
    </React.StrictMode>
  );
};
ButtonArea.propTypes = {
  children: PropTypes.node,
};

const SubmitButton = ({ label }) => {
  return (
    <React.StrictMode>
      <button type="submit" className="w-25 btn btn-primary me-auto">
        {label}
      </button>
    </React.StrictMode>
  );
};
SubmitButton.propTypes = {
  label: PropTypes.string,
};

const GoToButton = ({ label, url }) => {
  return (
    <React.StrictMode>
      <button
        type="button"
        className="w-25 btn btn-primary ma-auto float-right"
        onClick={() => {
          window.location.href = `${url}`;
        }}
      >
        {label}
      </button>
    </React.StrictMode>
  );
};
GoToButton.propTypes = {
  label: PropTypes.string,
  url: PropTypes.string,
};

const ErrorWindow = ({ errors }) => {
  // const errorDivClass = "d-block py-1 mb-2 alert alert-danger";
  const error = errors["non_field_errors"];
  return (
    <React.StrictMode>
      {typeof error == "undefined" ? null : (
        <>
          <div className={`${errorDivClass} ${divClass}`}>{error}</div>
          <div className="w-100" />
        </>
      )}
    </React.StrictMode>
  );
};
ErrorWindow.propTypes = {
  errors: PropTypes.object,
};

export const CsrfTokenInput = ({ csrfToken }) => {
  return <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />;
};
CsrfTokenInput.propTypes = {
  csrfToken: PropTypes.string,
};
