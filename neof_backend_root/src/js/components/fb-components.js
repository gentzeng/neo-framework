import React from "react";
import PropTypes from "prop-types";

export const PostResponsivenessWrapper = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="container">{children}</div>
    </React.StrictMode>
  );
};
PostResponsivenessWrapper.propTypes = {
  children: PropTypes.node,
};

export const Post = ({ _key, postData }) => {
  const { id, author_agent, time_since_creation } = postData;
  return (
    <React.StrictMode>
      <div className="row">
        <div className="col"></div>
        <div className="col mt-0 mb-3 fb-post-border" key={_key}>
          <div
            className={`card fb-post-container h-100 border-0 fb-post-border`}
          >
            <PostTop
              author_agent={author_agent}
              time_since_creation={time_since_creation}
            />
            <PostMiddle
              text={postData.text}
              image_low_quality={postData.image_low_quality}
              shared_text={postData.shared_text}
              shared_text_domain={postData.shared_text_domain}
            />
            {/* <PostBottom resourceType={resourceType} title={title} id={id} /> */}
          </div>
        </div>
        <div className="col"></div>
      </div>
    </React.StrictMode>
  );
};
Post.propTypes = {
  _key: PropTypes.number,
  postData: PropTypes.object,
  author_agent: PropTypes.object,
  id: PropTypes.number,
};

const PostTop = ({ author_agent, time_since_creation }) => {
  const {
    id,
    author_source,
    author,
    name,
    avatar_url,
    avatar,
    username,
    verified,
    link,
    bio,
    followers,
    following,
  } = author_agent;

  return (
    <React.StrictMode>
      <div className="card-header bg-white fb-post-header pb-0 border-bottom-0">
        <div className="d-flex">
          <div className="fb-post-avatar">
            <svg className="fb-post-avatar-svg" aria-hidden="true">
              <mask id="jsc_c_1m">
                <circle cx="20" cy="20" fill="white" r="20"></circle>
                <circle
                  cx="20"
                  cy="20"
                  fill="transparent"
                  r="17"
                  stroke="black"
                  strokeWidth="2"
                ></circle>
              </mask>
              <g>
                <image
                  x="4"
                  y="4"
                  height="100%"
                  width="100%"
                  // xlinkHref={`${avatar}`}
                ></image>
              </g>
            </svg>
          </div>
          <div className="flex-fill bg-white">
            <div className="fb-post-author">
              <div className="fb-post-author-rows">
                <span>
                  <h2 className="fb-h2">
                    <strong>
                      <span>{author.name}</span>
                    </strong>
                  </h2>
                </span>
              </div>
              <div className="fb-post-author-rows">
                <div className="fb-post-time">
                  {`${time_since_creation} Std.`}
                </div>
              </div>
            </div>
          </div>
          <div className="fb-post-options">
            <svg
              fill="currentColor"
              viewBox="0 0 20 20"
              width="1em"
              height="1em"
              className=""
            >
              <g fillRule="evenodd" transform="translate(-446 -350)">
                <path d="M458 360a2 2 0 1 1-4 0 2 2 0 0 1 4 0m6 0a2 2 0 1 1-4 0 2 2 0 0 1 4 0m-12 0a2 2 0 1 1-4 0 2 2 0 0 1 4 0"></path>
              </g>
            </svg>
          </div>
        </div>
      </div>
    </React.StrictMode>
  );
};
PostTop.propTypes = {
  author_agent: PropTypes.object,
};

const PostMiddle = ({
  text,
  image_low_quality,
  shared_text,
  shared_text_domain,
}) => {
  return (
    <React.StrictMode>
      <div className="card-body bg-white fb-post-body pb-0 border-bottom-0">
        <div className="fb-post-body-top">
          <div className="fb-post-body-text">{text}</div>
        </div>
        <div className="fb-post-media">
          <div className="fb-post-media-image">
            <img src={`${image_low_quality}`} width="500" />
          </div>
          <div className="fb-post-media-text">
            <div className="fb-post-media-link-domain">
              <span>{`${shared_text_domain}`}</span>
            </div>
            <div className="fb-post-media-shared-text">{`${shared_text}`}</div>
          </div>
        </div>
      </div>
    </React.StrictMode>
  );
};

PostMiddle.propTypes = {
  author_agent: PropTypes.object,
};
