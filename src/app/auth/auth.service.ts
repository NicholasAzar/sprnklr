import { Injectable } from '@angular/core';
import { AuthorizationRequest } from "@nicholasazar/appauth/built/authorization_request";
import { AuthorizationNotifier, AuthorizationRequestHandler } from "@nicholasazar/appauth/built/authorization_request_handler";
import { AuthorizationServiceConfiguration } from "@nicholasazar/appauth/built/authorization_service_configuration";
import { NodeCrypto } from '@nicholasazar/appauth/built/node_support/';
import { NodeBasedHandler } from "@nicholasazar/appauth/built/node_support/node_request_handler";
import { NodeRequestor } from "@nicholasazar/appauth/built/node_support/node_requestor";
import { GRANT_TYPE_AUTHORIZATION_CODE, GRANT_TYPE_REFRESH_TOKEN, TokenRequest } from "@nicholasazar/appauth/built/token_request";
import { BaseTokenRequestHandler, TokenRequestHandler } from "@nicholasazar/appauth/built/token_request_handler";
import { TokenResponse } from "@nicholasazar/appauth/built/token_response";
import { StringMap } from "@nicholasazar/appauth/built/types";
import { AppStoreService } from '../client-store/client-store.service';
import jwt_decode from 'jwt-decode';

const log = console.log;

/* the Node.js based HTTP client. */
const requestor = new NodeRequestor();

/* an example open id connect provider */
const openIdConnectUrl = "https://accounts.google.com";

/* example client configuration */
const clientId = "843314178188-aehtfrts58joh3skgprg7jikovr32l5j.apps.googleusercontent.com";
const redirectUri = "http://localhost:8000";
const scope = "openid email https://www.googleapis.com/auth/photoslibrary";

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private notifier: AuthorizationNotifier;
  private authorizationHandler: AuthorizationRequestHandler;
  private tokenHandler: TokenRequestHandler;

  // state
  private configuration: AuthorizationServiceConfiguration | undefined;

  constructor(private appStore:AppStoreService) {
    this.notifier = new AuthorizationNotifier();
    this.authorizationHandler = new NodeBasedHandler();
    this.tokenHandler = new BaseTokenRequestHandler(requestor);
    // set notifier to deliver responses
    this.authorizationHandler.setAuthorizationNotifier(this.notifier);
    // set a listener to listen for authorization responses
    // make refresh and access token requests.
    this.notifier.setAuthorizationListener((request, response, error) => {
      log("Authorization request complete ", request, response, error);
      if (response) {
        let codeVerifier: string | undefined;
        if(request.internal && request.internal.code_verifier) {
          codeVerifier = request.internal.code_verifier;
        }

        this.getTokens(response.code, codeVerifier);
          // .then(result => this.performWithFreshTokens());
      }
    });
  }

  fetchServiceConfiguration(): Promise<void> {
    return AuthorizationServiceConfiguration.fetchFromIssuer(
      openIdConnectUrl,
      requestor
    ).then(response => {
      log("Fetched service configuration", response);
      this.configuration = response;
    });
  }

  async startLogin(username?: string):Promise<void> {
    if (!this.configuration) {
      await this.fetchServiceConfiguration();
    }

    const extras: StringMap = { access_type: "offline" };
    if (username) {
      extras["login_hint"] = username;
    }

    // create a request
    const request = new AuthorizationRequest({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scope,
      response_type: AuthorizationRequest.RESPONSE_TYPE_CODE,
      state: undefined,
      extras: extras
    }, new NodeCrypto());

    log("Making authorization request ", this.configuration, request);

    return this.authorizationHandler.performAuthorizationRequest(
      this.configuration,
      request
    );
  }

  private getTokens(code: string, codeVerifier: string|undefined): Promise<void> {
    if (!this.configuration) {
      log("Unknown service configuration");
      return Promise.resolve();
    }

    const extras: StringMap = {};

    if(codeVerifier) {
      extras.code_verifier = codeVerifier;
    }

    // use the code to make the token request.
    let request = new TokenRequest({
      client_id: clientId,
      redirect_uri: redirectUri,
      grant_type: GRANT_TYPE_AUTHORIZATION_CODE,
      code: code,
      refresh_token: undefined,
      extras: extras
    });

    return this.tokenHandler
      .performTokenRequest(this.configuration, request)
      .then(response => {
        // log(`Refresh Token is ${response.refreshToken}`);
        log('Refresh token response: ', response);
        const decoded = jwt_decode(response.idToken);
        console.log('Decoded: ', decoded);
        this.appStore.addSourceAccount({
          email: decoded['email'],
          refreshToken: response.refreshToken,
          accessToken: response.accessToken,
          active:true,
          lastSync: null
        })
      });
  }

  // async startup():Promise<void> {
  //   await this.fetchServiceConfiguration();
  //   const refreshToken = this.store.get('refreshToken');
  //   if (refreshToken) {
  //     this.refreshToken = refreshToken;
  //     return this.performWithFreshTokens();
  //     });
  //   }
  //   return this.makeAuthorizationRequest();
  // }

  // loggedIn(): boolean {
  //   return !!this.accessTokenResponse && this.accessTokenResponse.isValid();
  // }


  // signOut() {
  //   // forget all cached token state
  //   this.accessTokenResponse = undefined;
  // }
  removeAccount() {
  }

  refreshTokens(email:string): Promise<void> {
    if (!this.configuration) {
      log("Unknown service configuration");
      return Promise.reject("Unknown service configuration");
    }

    const sourceAccount = this.appStore.getSourceAccount(email);

    if (!sourceAccount || !sourceAccount.refreshToken) {
      log("Missing refreshToken.");
      return Promise.reject("Missing refreshToken.");
    }
    // TODO(nzar): Check if the accessToken is still valid

    // if (this.accessTokenResponse && this.accessTokenResponse.isValid()) {
    //   // do nothing
    //   return Promise.resolve(this.accessTokenResponse.accessToken);
    // }
    let request = new TokenRequest({
      client_id: clientId,
      redirect_uri: redirectUri,
      grant_type: GRANT_TYPE_REFRESH_TOKEN,
      code: undefined,
      refresh_token: sourceAccount.refreshToken,
      extras: undefined
    });

    return this.tokenHandler
      .performTokenRequest(this.configuration, request)
      .then(response => {
        const decoded = jwt_decode(response.idToken);
        console.log('Decoded: ', decoded);
        this.appStore.replaceSourceAccount({
          email: decoded['email'],
          refreshToken: response.refreshToken,
          accessToken: response.accessToken,
          active:true,
          lastSync: null
        });
      });
  }
}
