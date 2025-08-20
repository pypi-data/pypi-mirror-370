<p align="center">
    <a href="https://quickbot.botforge.biz"><img src="https://quickbot.botforge.biz/img/qbot.svg" alt="QuickBot"></a>
</p>
<p align="center">
    <em>Telegram Bots Rapid Application Development (RAD) Framework.</em>
</p>

**QuickBot** is a library for fast development of Telegram bots and mini-apps following the **RAD (Rapid Application Development)** principle in a **declarative style**.

## Key Features

- **Automatic CRUD Interface Generation** – Manage objects effortlessly without manual UI coding.
- **Built-in Field Editors** – Includes text inputs, date/time pickers, boolean switches, enums, and entity selectors.
- **Advanced Pagination & Filtering** – Easily organize and navigate large datasets.
- **Authentication & Authorization** – Role-based access control for secure interactions.
- **Context Preservation** – Store navigation stacks and user interaction states in the database.
- **Internationalization Support** – Localizable UI and string fields for multilingual bots.

**QuickBot** powered by **[FastAPI](https://fastapi.tiangolo.com)**, **[SQLModel](https://sqlmodel.tiangolo.com)** & **[aiogram](https://aiogram.dev)** – Leverage the full capabilities of these frameworks for high performance and flexibility.

## Benefits

- **Faster Development** – Automate repetitive tasks and build bots in record time.
- **Highly Modular** – Easily extend and customize functionality.
- **Less Code Duplication** – Focus on core features while QuickBot handles the rest.
- **Enterprise-Grade Structure** – Scalable, maintainable, and optimized for real-world usage.

## Example
```python
class AppEntity(BotEntity):
    """
    BotEntity - business entity. Based on SQLModel, which provides ORM functionality,
    basic CRUD functions and additional metadata, describing entities view and behaviour
    """
    bot_entity_descriptor = Entity(         # metadata attribute
        name = "bot_entity",                # Entity - descriptor for entity metadata
        ...
    )

    name: str                               # entity field with default sqlmodel's FieldInfo descriptor
                                            # and default quickbot's field descriptor

    description: str | None = Field(        # field with sqlmodel's descriptor
        sa_type = String, index = True)     # and default quickbot's descriptor

    age: int = EntityField(                 # field with quickbot's descriptor
        caption = "Age",
    )

    user_id: int | None = EntityField(      # using both descriptors
        sm_descriptor=Field(
            sa_type=BigInteger,
            foreign_key="user.id",
            ondelete="RESTRICT",
            nullable=True,
        ),
        is_visible=False,
    )

    user: Optional[User] = EntityField(     # using Relationship as sqlmodel descriptor
        sm_descriptor=Relationship(
            back_populates="entities",
            sa_relationship_kwargs={
                "lazy": "selectin",
                "foreign_keys": "Entity.user_id",
            }
        ),
        caption="User",
    )


app = QuickBot()                             # bot application based on FastAPI application
                                            # providing Telegram API webhook handler

@app.command(                               # decorator for bot commands definition
    name="menu",
    caption="Main menu",
    show_in_bot_commands=True,              # shows command in bot's main menu
    clear_navigation=True,                  # resets navigation stack between bot dialogues
)
async def menu(context: CommandCallbackContext):
    context.message_text = "Main menu"      # message text
    context.keyboard_builder.row(           # and buttons will be shown to user
        InlineKeyboardButton(
            text="Entities",
            callback_data=ContextData(                  # callback query dataclass representing
                command=CallbackCommand.ENTITY_LIST,    # navigation context and its parameters
                entity_name="bot_entity"
            ).pack(),
        )
    )
```
## Result

<iframe width="100%" height="691" src="https://www.youtube.com/embed/ptTnoppkYfM" title="QuickBot Framework – The Open-Source RAD Tool for Telegram Bots" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Here you can see the result - [YouTube Video with Bot](https://www.youtube.com/shorts/ptTnoppkYfM)


