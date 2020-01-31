module Main exposing (main)

import Browser
import Html exposing (Html, pre, text)
import Http
import Json.Decode exposing (Decoder, field, list, map2, string)


main : Program () Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


type Model
    = Failure
    | Loading
    | Success (List Product)


init : () -> ( Model, Cmd Msg )
init _ =
    ( Loading
    , Http.get
        { url = "http://localhost:5000/products"
        , expect = Http.expectJson GotText (list productDecoder)
        }
    )


type alias Product =
    { id : String
    , title : String
    }


productDecoder : Decoder Product
productDecoder =
    map2
        Product
        (field "id" string)
        (field "title" string)


type Msg
    = GotText (Result Http.Error (List Product))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg _ =
    case msg of
        GotText result ->
            case result of
                Ok fulltext ->
                    ( Success fulltext, Cmd.none )

                Err _ ->
                    ( Failure, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none


view : Model -> Html Msg
view model =
    case model of
        Failure ->
            text "Http fetch failed"

        Loading ->
            text "Loading ..."

        Success fullText ->
            pre [] [ text (String.join ", " (List.map Debug.toString fullText)) ]
