export { getCookieValue as default };

export const getCookieValue = (name) => {
  return (
    document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)")?.pop() || ""
  );
};

export const deleteCookies = (hosts) => {
  hosts.map((host) => {
    document.cookie =
      "user_name" +
      `=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=${host};same_side=strict`;
    document.cookie =
      "auth_token" +
      `=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=${host};same_side=strict`;
  });
};

export const unauthorizedStatus = (status) => {
  if (status == 401 || status == 403) {
    return true;
  }
  return false;
};

const openLoginPage = () => {
  window.location.href = window.props.login;
  return;
};

export const openLoginPageIfUnauthorized = (response) => {
  if (!response.ok) {
    if (unauthorizedStatus(response.status)) {
      openLoginPage();
      return;
    }
  }
  return;
};

export const getUser = async () => {
  let _status = 200;
  let _json = {};
  const handleOnResponse = (response) => {
    if (response.status == 204) {
      // window.location.href = "/login"
    } else if (response.status == 401) {
      // window.location.href = "/login-researcher/";
      window.location.href = window.props.login;
      return {};
    }
    const json = response.json();
    return json;
  };
  await fetch("/api/auth/user/", {
    headers: {
      Accept: "application/json",
      Authorization: "Token " + getCookieValue("auth_token"),
    },
  })
    .then((response) => {
      _status = response.status;
      return handleOnResponse(response);
    })
    .then((json) => {
      _json = json;
    });
  // .catch((error) => console.error(error));

  return [_status, _json];
};
