import os

from airalogy.airalogy import Airalogy

os.environ["AIRALOGY_ENDPOINT"] = "http://localhost:4000"
os.environ["AIRALOGY_API_KEY"] = (
    "m0GqvQ/PqMgsaqWcykpP0Nx6f8+DrpoO/NVvLWKDcay1lPTCrjkdvsBJACBRR/jFyQyeBknS8FUV7UyDxxiwLYMxbh7U6H6KnScnEusaCF/F+WCoTgV5jrZPV0dw2pky"
)
os.environ["AIRALOGY_PROTOCOL_ID"] = (
    "airalogy.id.lab.lab1.project.proj1.protocol.test_node_sample.v.0.0.2"
)
airalogy = Airalogy()

# upload file
file = airalogy.upload_file_bytes("test.txt", b"test")
print(file)

# download file
print(airalogy.download_file_bytes(file["id"]))

# get file url
print(airalogy.get_file_url(file["id"]))

# download records
# print(
#     airalogy.download_records_json(
#         ["airalogy.id.record.01972062-22db-73f9-86f8-905515d3c88b.v.1"]
#     )
# )
