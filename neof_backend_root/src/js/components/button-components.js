import React from "react";
import PropTypes from "prop-types";

export { Button as default };

export const ButtonResponsivenessWrapper = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="row d-flex justity-content-center mx-0 mb-3">
        <div className="col-xxl-12 col-xl-12 col-lg-8 col-md-8 col-sm-10 col-8">
          {children}
        </div>
      </div>
    </React.StrictMode>
  );
};
ButtonResponsivenessWrapper.propTypes = {
  children: PropTypes.node,
};

export const DeleteButton = ({ style, onClick }) => {
  return (
    <React.StrictMode>
      <Button style={style} label={"Delete"} onClick={onClick} />
    </React.StrictMode>
  );
};
DeleteButton.propTypes = {
  style: PropTypes.object,
  onClick: PropTypes.func,
};

export const Button = ({ style, label, onClick }) => {
  return (
    <React.StrictMode>
      <button
        type="button"
        className={`btn btn-${style.color} ${style.textColor} me-2 `}
        onClick={onClick}
      >
        {label}
      </button>
    </React.StrictMode>
  );
};
Button.propTypes = {
  style: PropTypes.object,
  label: PropTypes.string,
  onClick: PropTypes.func,
};

export const FormSubmitButton = ({ style, label, formId }) => {
  return (
    <React.StrictMode>
      <button
        type="submit"
        form={formId}
        className={`btn btn-${style.color} ${style.textColor} me-2 `}
      >
        {label}
      </button>
    </React.StrictMode>
  );
};
FormSubmitButton.propTypes = {
  style: PropTypes.object,
  label: PropTypes.string,
  formId: PropTypes.string,
};
