from payloop import Payloop


def test_attribution():
    payloop = Payloop(api_key="abc")
    assert payloop.config.attribution is None

    payloop.attribution(
        parent_id=123,
        parent_uuid="f1cafd68-c438-4b6b-9c65-0e0199f9f549",
        parent_name="Abc",
        subsidiary_id=456,
        subsidiary_uuid="83d388a8-20ce-40d5-b48b-5ae2a7968b25",
        subsidiary_name="Def",
    )

    assert payloop.config.attribution == {
        "parent": {
            "id": 123,
            "name": "Abc",
            "uuid": "f1cafd68-c438-4b6b-9c65-0e0199f9f549",
        },
        "subsidiary": {
            "id": 456,
            "name": "Def",
            "uuid": "83d388a8-20ce-40d5-b48b-5ae2a7968b25",
        },
    }


def test_new_transaction():
    payloop = Payloop(api_key="abc")

    first_tx_uuid = payloop.config.tx_uuid
    assert first_tx_uuid is not None

    second_tx_uuid = payloop.new_transaction()
    assert second_tx_uuid is not None

    assert second_tx_uuid != first_tx_uuid
