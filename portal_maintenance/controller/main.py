# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import http, _
from operator import itemgetter
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class MaintancesData(CustomerPortal):

    def _prepare_portal_layout_values(self):
        domain, maintenance_count = [], 0
        values = super(MaintancesData, self)._prepare_portal_layout_values()
        employee_id = self.get_employeess()
        if employee_id:
            domain += [('id', 'in', employee_id.ids)]
            maintenance_count = request.env['maintenance.request'].sudo().search_count(domain)
        values['maintenance_count'] = maintenance_count
        values['page_name'] = 'maintenance'
        return values

    @http.route(['/get/maintenance', '/get/maintenance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_maintances(self, page=1, access_token=None, search=None, search_in='all', sortby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        maintenance_obj = request.env['maintenance.request']
        domain, maintenance_count, maintenance_ids = [], 0, None
        employee_id = request.env['maintenance.request'].sudo().search([])
        if employee_id:
            domain += [('id', 'in', employee_id.ids)]

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name asc'},
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'stage_id': {'label': _('Status'), 'order': 'stage_id desc'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'equipment_id': {'input': 'equipment_id', 'label': _('Search by Equipment')},
            'owner_user_id': {'input': 'owner_user_id', 'label': _('Search by Owner')},
            'schedule_date': {'input': 'schedule_date', 'label': _('Search by Date')},
            'name': {'input': 'name', 'label': _('Search By name')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage_id': {'input': 'stage_id', 'label': _('Status')},
        }

        if not sortby:
            sortby = 'id'
        order = searchbar_sortings[sortby]['order']

        # count for pager
        if employee_id:
            maintenance_count = maintenance_obj.search_count(domain)

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('equipment_id', 'all'):
                search_domain = OR([search_domain, [('equipment_id', 'ilike', search)]])
            if search_in in ('owner_user_id', 'all'):
                search_domain = OR([search_domain, [('owner_user_id', 'ilike', search)]])
            if search_in in ('schedule_date', 'all'):
                search_domain = OR([search_domain, [('schedule_date', 'like', search)]])
            domain += search_domain

        pager = portal_pager(
            url="/get/maintenance",
            total=maintenance_count,
            page=page,
            url_args={'search_in': search_in, 'search': search},
            step=12
        )

        grouped_maintenance = []
        # content according to pager and archive selected
        if employee_id:
            maintenance_ids = maintenance_obj.search(domain,  order=order, limit=12, offset=pager['offset'])
            request.session['my_expense_history'] = maintenance_ids.ids[:100]
            grouped_maintenance = [maintenance_ids]
            if groupby == 'stage_id':
                grouped_maintenance = [maintenance_obj.concat(*g) for k, g in groupbyelem(maintenance_ids, itemgetter('stage_id'))]

        values = {}
        values.update({
            'maintenance_ids': maintenance_ids,
            'page_name': 'maintenance',
            'maintenance_count': maintenance_count,
            'pager': pager,
            'default_url': '/get/maintenance',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search_in': search_in,
            'groupby': groupby,
            'grouped_maintenance': grouped_maintenance,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby
        })
        return request.render("portal_maintenance.portal_my_maintances", values)


    def get_employeess(self):
        return request.env['maintenance.request'].sudo().search([])


    @http.route('/delete/<model("maintenance.request"):work>/', auth='user', website=True)
    def deletemaintenance(self, work):
        work.unlink()
        return request.redirect('/get/maintenance')

    @http.route('/maintenance/<model("maintenance.request"):work>/', auth='user', website=True)
    def work(self, work):

        if work.schedule_date:
            ddd = str(work.schedule_date).split(' ')
            formated_date = ddd[0]+'T'+ddd[1][:-3]
        else:
            formated_date = False

        if work.duration:
            time = work.duration
            formated_duration = '{0:02.0f}:{1:02.0f}'.format(*divmod(time * 60, 60))
        else:
            formated_duration = False


        return request.render('portal_maintenance.maintenance_form_view', {
            'maintenance_id': work,
            'formated_date':formated_date,
            'formated_duration':formated_duration,
            })

    @http.route(['/student/form/update'], auth="user", website=True)
    def Student_Update(self,**kw):
        if kw.get('record'):
            if kw.get('schedule_date'):
                ddd = kw.get('schedule_date').split('T')
                formated_date = ddd[0] + " " + ddd[1]+':00'
            else:
                formated_date = False
            rec = kw.get('record')
            rec_id = http.request.env['maintenance.request'].sudo().search([('id','=',rec)])
            if kw.get('equipment_id'):
                e_id = kw.get('equipment_id')
            else:
                e_id = False
            rec_id.write({
                'name': kw.get('name'),
                'description' : kw.get('description'),
                'equipment_id' : e_id,
                'owner_user_id' : request.env.user.id,
                })
            if rec_id.schedule_date:
                ddd = str(rec_id.schedule_date).split(' ')
                formated_date = ddd[0]+'T'+ddd[1][:-3]
            else:
                formated_date = False

            return request.redirect("/maintenance/%s" % (slug(rec_id)))
        else:
            if kw.get('equipment_id') == 'blank':
                equipment_id = False
            else:
                equipment_id = request.env['maintenance.equipment'].sudo().search([('id','=',kw.get('equipment_id'))])
            res = request.env['maintenance.request'].create({
                'name': kw.get('name'),
                'description' : kw.get('description'),
                'equipment_id' : equipment_id and equipment_id.id or False,
                'owner_user_id' : request.env.user.id,
                })
            if res.schedule_date:
                ddd = str(res.schedule_date).split(' ')
                formated_date = ddd[0]+'T'+ddd[1][:-3]
            else:
                formated_date = False
            return request.redirect('/get/maintenance')

    @http.route(['/maintenance/create'], auth="user", website=True)
    def maintenance_create(self,**kw):
        return request.render('portal_maintenance.maintenance_form_view',{'page_name':'create'})

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['maintenance_count'] = request.env['maintenance.request'].sudo().search_count([])
        return values