import React from "react";
import PropTypes from "prop-types";

export { ModalCallButton as default };

export const ModalCallButton = ({ target, style, label }) => {
  const { color, textColor } = style;
  return (
    <React.StrictMode>
      <button
        type="button"
        className={`btn btn-${color} ${textColor} me-2`}
        data-bs-toggle="modal"
        data-bs-target={`#${target}`}
      >
        {label}
      </button>
    </React.StrictMode>
  );
};
ModalCallButton.propTypes = {
  target: PropTypes.string,
  style: PropTypes.object,
  color: PropTypes.string,
  textColor: PropTypes.string,
  label: PropTypes.string,
};

export const Modal = ({ id, title, confirmButton, children }) => {
  return (
    <div
      id={`${id}`}
      className="modal fade"
      tabIndex="-1"
      aria-labelledby="modalComponentLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-dialog-scrollable modal-fullscreen">
        <div className="modal-content">
          <ModalHeader title={title} />
          <ModalBody>{children}</ModalBody>
          <ModalFooter>
            <ModalDismissButton />
            {confirmButton}
          </ModalFooter>
        </div>
      </div>
    </div>
  );
};
Modal.propTypes = {
  id: PropTypes.string,
  title: PropTypes.string,
  confirmButton: PropTypes.element,
  children: PropTypes.node,
};

const ModalHeader = ({ title }) => {
  return (
    <React.StrictMode>
      <div className="modal-header">
        <h5 className="modal-title" id="modalComponentLabel">
          {title}
        </h5>
        <button
          type="button"
          className="btn-close"
          data-bs-dismiss="modal"
          aria-label="Close"
        ></button>
      </div>
    </React.StrictMode>
  );
};
ModalHeader.propTypes = {
  title: PropTypes.string,
};

const ModalBody = ({ children }) => {
  return <div className="modal-body">{children}</div>;
};
ModalBody.propTypes = {
  children: PropTypes.node,
};

const ModalFooter = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="modal-footer">{children}</div>
    </React.StrictMode>
  );
};
ModalFooter.propTypes = {
  children: PropTypes.node,
};

const ModalDismissButton = () => {
  return (
    <React.StrictMode>
      <button
        type="button"
        className="btn btn-secondary"
        data-bs-dismiss="modal"
      >
        Close
      </button>
    </React.StrictMode>
  );
};

export const ModalSubmitButton = ({ style, label, formId }) => {
  return (
    <React.StrictMode>
      <button
        type="submit"
        form={formId}
        className={`btn btn-${style.color}`}
        data-bs-dismiss="modal"
      >
        {label}
      </button>
    </React.StrictMode>
  );
};
ModalSubmitButton.propTypes = {
  style: PropTypes.object,
  label: PropTypes.string,
  formId: PropTypes.string,
};
