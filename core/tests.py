from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, MagicMock
from datetime import time

from core import views


class InscricaoTurnoViewTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def _make_request(self, path, user_id=123, user_tipo="aluno"):
		request = self.factory.get(path)
		request.session = {"user_id": user_id, "user_tipo": user_tipo}
		# messages storage
		from django.contrib.messages.storage.fallback import FallbackStorage
		setattr(request, "_messages", FallbackStorage(request))
		return request

	@patch("core.views.InscricaoTurno.objects")
	@patch("core.views.TurnoUc.objects")
	@patch("core.views.get_object_or_404")
	@patch("core.views.validar_inscricao_disponivel")
	def test_inscrever_turno_uc_errada(self, mock_validar, mock_get, mock_tuc, mock_insc):
		mock_validar.return_value = (True, "")

		aluno = MagicMock(id_curso_id=1, n_mecanografico=123)
		turno = MagicMock(id_turno=10, tipo="TP", capacidade=10)
		uc = MagicMock(id_unidadecurricular=5, nome="UC X")
		mock_get.side_effect = [aluno, turno, uc]

		mock_tuc.filter.return_value.exists.return_value = False

		request = self._make_request("/turnos/inscrever/10/5/")
		response = views.inscrever_turno(request, 10, 5)

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("home:inscricao_turno"), response.url)

	@patch("core.views.InscricaoTurno.objects")
	@patch("core.views.TurnoUc.objects")
	@patch("core.views.get_object_or_404")
	@patch("core.views.validar_inscricao_disponivel")
	def test_inscrever_turno_cheio(self, mock_validar, mock_get, mock_tuc, mock_insc):
		mock_validar.return_value = (True, "")

		aluno = MagicMock(id_curso_id=1, n_mecanografico=123)
		turno = MagicMock(id_turno=10, tipo="TP", capacidade=1)
		uc = MagicMock(id_unidadecurricular=5, nome="UC X")
		mock_get.side_effect = [aluno, turno, uc]

		mock_tuc.filter.return_value.exists.return_value = True
		mock_insc.filter.return_value.count.return_value = 1  # igual à capacidade

		request = self._make_request("/turnos/inscrever/10/5/")
		response = views.inscrever_turno(request, 10, 5)

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("home:inscricao_turno"), response.url)

	@patch("core.views.InscricaoTurno.objects")
	@patch("core.views.TurnoUc.objects")
	@patch("core.views.get_object_or_404")
	def test_inscrever_turno_aluno_outro_curso(self, mock_get, mock_tuc, mock_insc):
		aluno = MagicMock(id_curso_id=2, n_mecanografico=123)
		mock_get.side_effect = [aluno]

		request = self._make_request("/turnos/inscrever/10/5/")
		response = views.inscrever_turno(request, 10, 5)

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("home:index"), response.url)


class ApiConflitosTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def _make_request(self, path, user_id=123, user_tipo="aluno"):
		request = self.factory.get(path)
		request.session = {"user_id": user_id, "user_tipo": user_tipo}
		return request

	@patch("core.views.InscricaoTurno.objects")
	@patch("core.views.TurnoUc.objects")
	@patch("core.views.get_object_or_404")
	def test_conflito_dias_diferentes_nao_reporta(self, mock_get, mock_tuc, mock_insc):
		aluno = MagicMock()
		turno_novo = MagicMock()
		mock_get.side_effect = [aluno, turno_novo]

		turno_uc_novo = MagicMock(hora_inicio=time(8, 0), hora_fim=time(10, 0), dia="Segunda")
		mock_tuc.filter.return_value.exists.return_value = True
		mock_tuc.filter.return_value.__iter__.return_value = [turno_uc_novo]
		mock_tuc.filter.return_value.first.return_value = turno_uc_novo

		insc = MagicMock()
		insc.id_turno = MagicMock()
		insc.id_unidadecurricular = MagicMock(nome="Outra UC")
		mock_insc.filter.return_value.select_related.return_value = [insc]

		turno_uc_existente = MagicMock(hora_inicio=time(8, 30), hora_fim=time(9, 30), dia="Terça")
		# Segunda chamada ao filter (para o turno existente)
		def filter_side_effect(*args, **kwargs):
			if kwargs.get('id_turno') == turno_novo:
				return mock_tuc.filter.return_value
			return MagicMock(first=MagicMock(return_value=turno_uc_existente))

		mock_tuc.filter.side_effect = filter_side_effect

		request = self._make_request("/api/turnos/conflitos/10/")
		response = views.api_verificar_conflitos(request, 10)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data["conflitos"], [])
