module Main exposing (main)

import Browser exposing (Document)
import Html exposing (Html, pre, text)
import Http
import Json.Decode exposing (Decoder, field, int, list, map2, string)


main : Program () Model Msg
main =
    Browser.document
        { init = init
        , view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        }


type Model
    = Failure
    | Loading
    | Success (List ArticleShort)


init : flags -> ( Model, Cmd Msg )
init _ =
    ( Loading
    , Http.get
        { url = "http://localhost:8000/articles"
        , expect = Http.expectJson GotText (list articleShortDecoder)
        }
    )


type alias ArticleShort =
    { id : Int
    , title : String
    }



-- type alias Article =
--     { id : Int
--     , title : String
--     , content : String
--     , created_by : Int
--     , time_created : String
--     }


articleShortDecoder : Decoder ArticleShort
articleShortDecoder =
    map2
        ArticleShort
        (field "id" int)
        (field "title" string)


type Msg
    = GotText (Result Http.Error (List ArticleShort))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg _ =
    case msg of
        GotText result ->
            case result of
                Ok fulltext ->
                    ( Success fulltext, Cmd.none )

                Err _ ->
                    ( Failure, Cmd.none )


view : Model -> Document Msg
view model =
    { title = "Wiki"
    , body = [ mainView model ]
    }


mainView : Model -> Html Msg
mainView model =
    case model of
        Failure ->
            text "Http fetch failed"

        Loading ->
            text "Loading ..."

        Success fullText ->
            pre [] [ text <| String.join ", " <| List.map Debug.toString fullText ]
