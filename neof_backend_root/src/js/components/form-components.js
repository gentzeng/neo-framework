import React from "react";
import PropTypes from "prop-types";
import CsrfTokenInput from "../utils/authentication-utils";
import { toKeyValueArray } from "../utils/dictionary-utils";
import { restCreate } from "../api/rest-api-consumation";
import capitalizeFirstLetter from "../utils/string-utils";

export { CreateForm as default };

export const CreateForm = ({ id, dataState, csrfToken, createFields }) => {
  const resourceUrl = dataState["resource"].url;
  const setStateCallback = dataState["resource"].callback;

  const foreignKeyValue = window.sessionStorage.getItem("foreignKey");
  const fields = toKeyValueArray(createFields);
  const onSubmit = async (event) => {
    event.preventDefault(); // prevent default behavior of form submit

    const [
      ,
      // status
      json,
    ] = await restCreate({
      url: resourceUrl,
      data: new FormData(event.target),
    });
    setStateCallback((oldStatus) => [...oldStatus, json]);
  };

  return (
    <form onSubmit={onSubmit} id={id}>
      <CsrfTokenInput csrfToken={csrfToken} />
      <input
        type="hidden"
        name="foreignKey"
        value={foreignKeyValue == null ? "" : foreignKeyValue}
      />

      {fields.map((field) => {
        return <FormField key={field[0]} field={field} />;
      })}
    </form>
  );
};
CreateForm.propTypes = {
  id: PropTypes.string,
  dataState: PropTypes.object,
  resourceUrl: PropTypes.string,
  setStateCallback: PropTypes.func,
  csrfToken: PropTypes.string,
  createFields: PropTypes.object,
};

const FormField = ({ field }) => {
  const fieldName = field[0];
  const inputId = `id${fieldName}`;
  const label = capitalizeFirstLetter(fieldName.replace(/_/g, " "));
  return (
    <div className="mb-3 row">
      <label className="col-form-label px-3" htmlFor={inputId}>
        {label}
      </label>
      <FormFieldTag inputId={inputId} field={field} />
    </div>
  );
};
FormField.propTypes = {
  field: PropTypes.array,
};

const FormFieldTag = ({ inputId, field }) => {
  const fieldName = field[0];
  const fieldProps = field[1];
  const fieldTagType = fieldProps.htmlTag;
  if (fieldTagType === "textarea") {
    return (
      <textarea
        id={inputId}
        name={fieldName}
        type={fieldProps.type}
        className=" form-control mx-3"
        autoComplete="on"
      />
    );
  }
  return (
    <input
      id={inputId}
      name={fieldName}
      type={fieldProps.type}
      className="form-control mx-3"
      autoComplete="on"
    />
  );
};
FormFieldTag.propTypes = {
  inputId: PropTypes.string,
  field: PropTypes.array,
};
