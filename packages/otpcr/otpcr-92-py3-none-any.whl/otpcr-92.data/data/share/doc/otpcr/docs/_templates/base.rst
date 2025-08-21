.. _{{ fullname }}:


.. title:: {{ fullname }}


.. raw:: html

    <br>
    <center>
    <b>

:ref:`src <source>`/**{{ name }}**

.. raw:: html

    </b>
    </center>


.. auto{{ objtype }}:: {{ fullname }}
    :members:
    :private-members:
    :undoc-members:

    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: exceptions

    .. autosummary::
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block classes %}
    {% if classes %}
    .. rubric:: classes

    .. autosummary:: 
    {% for item in classes %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block functions %}
    {% if functions %}
    .. rubric:: functions

    .. autosummary::
    {% for item in functions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    .. raw:: html

        <br><br>


.. currentmodule:: {{ fullname }}
