let DEBUG = false;
let host = "http://localhost:8000";
let stripePublishKey = "pk_test_fNvM4Ol4vGCCBEXfhtkVu91v00qKo5oSrQ";
if (DEBUG === false) {
  host = "http://localhost:8000";
  stripePublishKey = "pk_test_fNvM4Ol4vGCCBEXfhtkVu91v00qKo5oSrQ";
}

export { stripePublishKey };

export const APIEndpoint = `http://localhost:8000/api`;

export const fileUploadURL = `${APIEndpoint}/demo/`;
export const facialRecognitionURL = `${APIEndpoint}/upload/`;
export const emailURL = `${APIEndpoint}/email/`;
export const changeEmailURL = `${APIEndpoint}/change-email/`;
export const changePasswordURL = `${APIEndpoint}/change-password/`;
export const billingURL = `${APIEndpoint}/billing/`;
export const subscribeURL = `${APIEndpoint}/subscribe/`;
export const APIkeyURL = `${APIEndpoint}/api-key/`;
export const cancelSubscriptionURL = `${APIEndpoint}/cancel-subscription/`;

export const loginURL = `http://localhost:8000/rest-auth/login/`;
export const signupURL = `http://localhost:8000/rest-auth/registration/`;
