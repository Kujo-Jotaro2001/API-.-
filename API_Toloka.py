import requests

url_projects = "https://sandbox.toloka.yandex.com/api/v1/projects"
url_pools = "https://sandbox.toloka.yandex.com/api/v1/pools"
url_tasks = "https://sandbox.toloka.yandex.com/api/v1/tasks"

auth_token = ""
headers = {'Authorization': f"OAuth {auth_token}", "Content-type": "application/JSON"}

project_data = {
    "public_name": "Выделите все дорожные знаки на картинке (Final launch)",
    "public_description": "Посмотрите на фото и выделите все дорожные дорожные знаки.",
    "public_instructions": "Найдите на фото все дорожные знаки и выделите их в отдельные рамки.",
    "private_comment": "ismail2001",
    "task_spec": {
        "input_spec": {
            "image": {
                "type": "URL",
                "required": True,
                "hidden": False
            }
        },
        "output_spec": {
            "result": {
                "type": "json",
                "required": True,
                "hidden": False
            }
        },
        "view_spec": {
            "assets": {
                "script_urls": ["$TOLOKA_ASSETS/js/toloka-handlebars-templates.js",
                                "$TOLOKA_ASSETS/js/image-annotation.js"]
            },
            "markup": """{{field type="image-annotation" name="result" src=image}}""",
            "script": """exports.Task = extend(TolokaHandlebarsTask, function (options) {
  TolokaHandlebarsTask.call(this, options);
}, {
  onRender: function() {
    // DOM element for task is formed (available via #getDOMElement()) 
  },
  onDestroy: function() {
    // Task is completed. Global resources can be released (if used)
  }
});

function extend(ParentClass, constructorFunction, prototypeHash) {
  constructorFunction = constructorFunction || function () {};
  prototypeHash = prototypeHash || {};
  if (ParentClass) {
    constructorFunction.prototype = Object.create(ParentClass.prototype);
  }
  for (var i in prototypeHash) {
    constructorFunction.prototype[i] = prototypeHash[i];
  }
  return constructorFunction;
}""",
            "styles": """/* disable rectangle-editor controls */
.image-annotation-editor__shape-rectangle {
  display: none;
}""",
            "settings": {
                "showSkip": True,
                "showTimer": True,
                "showTitle": True,
                "showSubmit": True,
                "showFullscreen": True,
                "showInstructions": True,
                "showFinish": True,
                "showMessage": True,
                "showReward": True
            }
        }
    },
    "assignments_issuing_type": "AUTOMATED",
    "assignments_automerge_enabled": False,
    "max_active_assignments_count": 15,
    "localization_config": {
        "default_language": "RU"
    }
}

project_response = requests.post(url=url_projects, headers=headers, json=project_data)
print(project_response.json())
project_id = requests.get(url=url_projects, headers=headers).json()["items"][0]["id"]

pool_data = {
    "project_id": project_id,
    "private_name": "Разметка дорожных знаков на фото попытка (this is a final launch)",
    "private_comment": "ismail2001",
    "public_description": "Посмотрите на картинку и выделите все дорожные знаки в отдельные рамки",
    "may_contain_adult_content": False,
    "will_expire": "2021-09-30T13:00",
    "reward_per_assignment": 0.05,
    "assignment_max_duration_seconds": 300,
    "auto_accept_solutions": True,
    "auto_accept_period_day": 7,
    "assignments_issuing_config": {
        "issue_task_suites_in_creation_order": False
    },
    "filter": {
        "and": [{
            "or": [{
                "category": "profile",
                "key": "country",
                "operator": "EQ",
                "value": "RU"
            }]
        }, {
            "or": [{
                "category": "profile",
                "key": "city",
                "value": 213,
                "operator": "IN"
            }]
        }]
    },
    "quality_control": {
        "configs": [
            {
                "collector_config": {
                    "type": "ASSIGNMENT_SUBMIT_TIME",
                    "parameters": {
                        "history_size": 10,
                        "fast_submit_threshold_seconds": 3
                    }
                },
                "rules": [
                    {
                        "conditions": [
                            {
                                "key": "total_submitted_count",
                                "operator": "EQ",
                                "value": 10
                            },
                            {
                                "key": "fast_submitted_count",
                                "operator": "GTE",
                                "value": 4
                            }
                        ],
                        "action": {
                            "type": "RESTRICTION_V2",
                            "parameters": {
                                "scope": "PROJECT",
                                "duration_unit": "DAYS",
                                "duration": 7,
                                "private_comment": "4 или более быстрых ответа подряд"
                            }
                        }
                    }
                ]
            },
            {
                "collector_config": {
                    "type": "SKIPPED_IN_ROW_ASSIGNMENTS"
                },
                "rules": [{
                    "conditions": [{
                        "key": "skipped_in_row_count",
                        "operator": "GTE",
                        "value": 10
                    }],
                    "action": {
                        "type": "RESTRICTION_V2",
                        "parameters": {
                            "scope": "PROJECT",
                            "duration_unit": "DAYS",
                            "duration": 7,
                            "private_comment": "Пропущено 10 или более страниц подряд"
                        }
                    }
                }]
            }
        ]
    },
    "defaults": {
        "default_overlap_for_new_task_suites": 1,
        "default_overlap_for_new_tasks": 1
    },
    "mixer_config": {
        "real_tasks_count": 1,
        "golden_tasks_count": 0,
        "training_tasks_count": 0,
        "min_real_tasks_count": 1,
        "min_golden_tasks_count": 0,
        "min_training_tasks_count": 0,
        "force_last_assignment": True,
        "force_last_assignment_delay_seconds": 10,
        "mix_tasks_in_creation_order": True,
        "shuffle_tasks_in_task_suite": False,
    },
    "priority": 10,
}

pool = requests.post(url=url_pools, headers=headers, json=pool_data)
print(pool.json())
pool_id = requests.get(url=f"{url_pools}?project_id={project_id}", headers=headers).json()["items"][-1]["id"]
tasks = []

with open("//Users//ismail2001//Desktop//tasks.tsv", "r", encoding="utf-8") as in_file:
    files = in_file.readlines()
    files.pop()
    for image_url in files[1:]:
        tasks.append({"input_values": {"image": image_url.strip()}, "pool_id": pool_id, "overlap": 1})

task_response = requests.post(url=url_tasks, headers=headers, json=tasks)
print(task_response.json())
