from court_auction_insights.cli import build_parser


def test_cli_exposes_expected_commands():
    parser = build_parser()
    assert parser.parse_args(["init-db"]).command == "init-db"
    assert parser.parse_args(["worker-once"]).command == "worker-once"
    assert parser.parse_args(["serve"]).command == "serve"
