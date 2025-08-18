import pytest


@pytest.mark.skip(reason="Fabric is not available")
def test_integration_fabric_data_agent_client(fabric_info):
    from fabric.dataagent.client import (
        FabricOpenAI,
        Fabricdata_agentAPI,
        Fabricdata_agentManagement,
    )
    from sempy.fabric import list_items

    # oai = FabricOpenAI("20250113-dax-1")

    # t = oai.beta.threads.create()
    # print(f"thread id: {t.id}")

    # client_api = Fabricdata_agentAPI(fabric_info["workspace_id"])
    # client = Fabricdata_agentAPI("20250113-dax-1")

    mgmt = Fabricdata_agentManagement("20250113-dax-1")

    print(mgmt.get_configuration())

    datasources = mgmt.get_datasources()

    # datasources[1].pretty_print()
    datasources[0].pretty_print()

    datasources[0].unselect("Platforms")

    datasources[0].pretty_print()
    # print(datasources[0].get_fewshots())

    # datasources[1].remove_fewshot("736359b3-3ebd-4d42-9e06-30e76ded3569")
    # print(datasources[1].get_fewshots())

    # datasources[1].add_fewshot("test5", "SELECT * from dbo.factfinance")

    # print(datasources[1].get_fewshots())

    # ds = mgmt.add_datasource("AdventureWorksLH", "ML-SHARED-data_agentV2-DATASOURCES", type="lakehouse")

    # fw = ds.get_fewshots()

    # ds.unselect()
    # ds.select("dbo", "factfinance")

    # ds.pretty_print()

    # mgmt.remove_datasource("AdventureWorksLH")

    # config = client.get_configuration()

    # print(config)
    # # c2 = client.set_configuration(config)
    # # c3 = client.set_configuration(c2)
    # # print(c3)

    # datasources = client.get_datasources()

    # print(datasources)

    # datasources[0].value["additional_instructions"] = "Make sure each column is prefixed with YY_"

    # # datasources[0] = client.set_datasource(datasources[0])

    # print(client.get_schema("9c5aa981-58eb-4844-954b-8546e137dfa3", "eee0500b-0616-4f25-8d80-faf0e2813658", "Kusto"))

    # # client2 = FabricA()

    # # client2.update_configuration(instructions="", userDescription="")

    # # client2.deploy() # deploy the AI skill (sandbox -> production)

    # # datasources = client2.get_datasources()

    # # calls are effective immediately

    # # datasources[0].pretty_print() ## tree view in notebook
    # # datasources[0].update_configuration(instructions="Make sure each column is prefixed with YY_", schema_mode="schema", user_description="7th Generation Video Games")
    # # datasources[0].select(["Games", "Id"])
    # # datasources[0].select(["dbo", "Games", "Name"])
    # # datasources[0].unselect("Games")

    # # automatically add to AI skill, unselect all tables
    # # new_datasource = client2.add_datasource(artifact_name_or_id="", workspace_id_or_name="", type="Kusto"|None)
